# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import TYPE_CHECKING

import paddle
from paddle.jit.dy2static.utils import compose_guards
from paddle.utils import to_sequence

from ..utils import (
    InnerError,
    log_do,
    map_if,
    map_if_extend,
)
from .statement_ir import (
    ParametersHolder,
    StatementContext,
    StatementContextRegistry,
    Symbol,
)

if TYPE_CHECKING:
    from .builder import StatementIRBuilder
    from .statement_ir import Statement, StatementIR


def replace_symbol(
    values: list[Symbol] | list[object], state: dict[str, Symbol]
):
    """
    Replaces Symbol objects with their corresponding values.

    Args:
        values: A list of values that may contain Symbol objects.
        state: A dict mapping Symbol names to their corresponding values.

    Returns:
        A new list with Symbol objects replaced by their corresponding values in the state dict.
    """
    # deal with list / map etc.
    values = map_if_extend(
        values,
        pred=lambda x: isinstance(x, Symbol),
        true_fn=lambda x: state[x.name],
        false_fn=lambda x: x,
    )
    return values


def _append_opstack_between(start, end, stack):
    # The range is [start, end)
    for op in for_each_ops_between(start, end):
        op.callstack = stack


def for_each_ops_between(start, end):
    # [start, end)
    program = paddle.static.default_main_program()
    ops = program.global_block().ops[start:end]
    yield from ops


def opnum_in_program():
    program = paddle.static.default_main_program()
    return len(program.global_block().ops)


class Interpreter:
    """
    Interpreter is used to interpret and execute SIR.
    """

    def __init__(self, builder: StatementIRBuilder):
        self._builder = builder

    def get_sir(self, name: str) -> StatementIR:
        """
        Returns the StatementIR object by given name.

        Args:
            name: The name of the StatementIR.

        Returns:
            The StatementIR object with the given name.
        """
        return self._builder.get_sir(name)

    def run_sir(self, name: str, state: dict[str, Symbol]):
        """
        Runs the StatementIR with the given name using the provided state.

        Args:
            name: The name of the given StatementIR to run.
            state: A dict mapping Symbol names to their corresponding values.

        Returns:
            A list of the Symbol of the StatementIR after execution.
        """

        def _set(v, s):
            state[s.name] = v

        SIR = self.get_sir(name)
        for stmt in SIR.statements:
            stmt: Statement
            before_stmt_opnum = opnum_in_program()
            inputs = replace_symbol(stmt.inputs, state)

            with create_context_guard(stmt.contexts)():
                outs = getattr(self, stmt.type)(stmt, inputs)

            if len(to_sequence(outs)) != len(to_sequence(stmt.outputs)):
                raise InnerError("Number output mismatch, some error happen.")

            log_do(
                3,
                lambda: _append_opstack_between(
                    before_stmt_opnum, opnum_in_program() + 1, stmt.stmt_stack
                ),
            )

            map_if(
                outs,
                stmt.outputs,
                pred=lambda v, s: isinstance(s, Symbol),
                true_fn=lambda v, s: _set(v, s),
                false_fn=lambda v, s: None,
            )
        # fetch outputs
        return replace_symbol(SIR.outputs, state)

    def api(self, stmt, inputs):
        args, kwargs = inputs
        return stmt.api(*args, **kwargs)

    def method(self, stmt, inputs):
        args, kwargs = inputs
        var = args[0]
        return getattr(var, stmt.method)(*args[1:], **kwargs)

    def layer(self, stmt, inputs):
        args, kwargs = inputs
        layer = stmt.layer()
        assert layer is not None, "SIR bound layer is None."
        return layer(*args, **kwargs)

    def AST(self, stmt, inputs):
        args, kwargs = inputs
        return stmt.converted_func(*args, **kwargs)


def compile_sir(
    builder: StatementIRBuilder, name: str, parameters_holder: ParametersHolder
):
    """
    Compile a SIR to a new function

    Args:
        context: The context to compile
        name: The name of the sir to compile

    """

    @paddle.jit.not_to_static
    def wrapper(args):
        """
        This function will be decorated by paddle.to_static.
        so the args is variables, not eager tensors.
        """
        interpreter = Interpreter(builder)
        SIR = interpreter.get_sir(name)
        state = prepare_state(SIR, args, parameters_holder)
        return interpreter.run_sir(name, state)

    return wrapper


def prepare_state(
    SIR: StatementIR, inputs, parameters_holder: ParametersHolder
):
    state = {}
    # bind inputs
    assert len(SIR.inputs) == len(inputs), "Inputs length mismatch."
    for sir_inp, inp in zip(SIR.inputs, inputs):
        state[sir_inp.name] = inp

    for sir_param in SIR.params:
        state[sir_param.name] = paddle.base.dygraph.base._convert_into_variable(
            parameters_holder.get(sir_param.name)
        )

    return state


def create_context_guard(contexts: list[StatementContext]):
    guards = list(
        map(
            lambda ctx: (
                lambda: StatementContextRegistry.get_context_guard(type(ctx))(
                    ctx
                )
            ),
            contexts,
        )
    )
    return compose_guards(*guards)
