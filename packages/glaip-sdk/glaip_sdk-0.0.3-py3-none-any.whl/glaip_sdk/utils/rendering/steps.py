"""Rendering utilities.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from collections.abc import Iterator

from .models import Step


class StepManager:
    def __init__(self, max_steps: int = 200):
        self.by_id: dict[str, Step] = {}
        self.order: list[str] = []
        self.children: dict[str, list[str]] = {}
        self.key_index: dict[tuple, str] = {}
        self.slot_counter: dict[tuple, int] = {}
        self.max_steps = max_steps
        self._last_running: dict[tuple, str] = {}

    def _alloc_slot(self, task_id, context_id, kind, name) -> int:
        k = (task_id, context_id, kind, name)
        self.slot_counter[k] = self.slot_counter.get(k, 0) + 1
        return self.slot_counter[k]

    def _key(self, task_id, context_id, kind, name, slot) -> tuple:
        return (task_id, context_id, kind, name, slot)

    def _make_id(self, task_id, context_id, kind, name, slot) -> str:
        return f"{task_id or 't'}::{context_id or 'c'}::{kind}::{name}::{slot}"

    def start_or_get(
        self, *, task_id, context_id, kind, name, parent_id=None, args=None
    ) -> Step:
        existing = self.find_running(
            task_id=task_id, context_id=context_id, kind=kind, name=name
        )
        if existing:
            if args and existing.args != args:
                existing.args = args
            return existing
        slot = self._alloc_slot(task_id, context_id, kind, name)
        key = self._key(task_id, context_id, kind, name, slot)
        step_id = self._make_id(task_id, context_id, kind, name, slot)
        st = Step(
            step_id=step_id,
            kind=kind,
            name=name,
            parent_id=parent_id,
            task_id=task_id,
            context_id=context_id,
            args=args or {},
        )
        self.by_id[step_id] = st
        if parent_id:
            self.children.setdefault(parent_id, []).append(step_id)
        else:
            self.order.append(step_id)
        self.key_index[key] = step_id
        self._prune_steps()
        self._last_running[(task_id, context_id, kind, name)] = step_id
        return st

    def _prune_steps(self):
        total = len(self.order) + sum(len(v) for v in self.children.values())
        if total <= self.max_steps:
            return

        def remove_subtree(root_id: str):
            stack = [root_id]
            to_remove = []
            while stack:
                sid = stack.pop()
                to_remove.append(sid)
                stack.extend(self.children.pop(sid, []))
            for sid in to_remove:
                st = self.by_id.pop(sid, None)
                if st:
                    key = (st.task_id, st.context_id, st.kind, st.name)
                    self._last_running.pop(key, None)
                for _parent, kids in list(self.children.items()):
                    if sid in kids:
                        kids.remove(sid)
                if sid in self.order:
                    self.order.remove(sid)

        while total > self.max_steps and self.order:
            sid = self.order[0]
            subtree = [sid]
            stack = list(self.children.get(sid, []))
            while stack:
                x = stack.pop()
                subtree.append(x)
                stack.extend(self.children.get(x, []))
            total -= len(subtree)
            remove_subtree(sid)

    def get_child_count(self, step_id: str) -> int:
        return len(self.children.get(step_id, []))

    def find_running(self, *, task_id, context_id, kind, name) -> Step | None:
        key = (task_id, context_id, kind, name)
        step_id = self._last_running.get(key)
        if step_id:
            st = self.by_id.get(step_id)
            if st and st.status != "finished":
                return st
        for sid in reversed(list(self._iter_all_steps())):
            st = self.by_id.get(sid)
            if (
                st
                and (st.task_id, st.context_id, st.kind, st.name)
                == (
                    task_id,
                    context_id,
                    kind,
                    name,
                )
                and st.status != "finished"
            ):
                return st
        return None

    def finish(
        self, *, task_id, context_id, kind, name, output=None, duration_raw=None
    ):
        st = self.find_running(
            task_id=task_id, context_id=context_id, kind=kind, name=name
        )
        if not st:
            # Try to find any existing step with matching parameters, even if not running
            for sid in reversed(list(self._iter_all_steps())):
                st_check = self.by_id.get(sid)
                if (
                    st_check
                    and st_check.task_id == task_id
                    and st_check.context_id == context_id
                    and st_check.kind == kind
                    and st_check.name == name
                ):
                    st = st_check
                    break

            # If still no step found, create a new one
            if not st:
                st = self.start_or_get(
                    task_id=task_id, context_id=context_id, kind=kind, name=name
                )

        if output:
            st.output = output
        st.finish(duration_raw)
        key = (task_id, context_id, kind, name)
        if self._last_running.get(key) == st.step_id:
            self._last_running.pop(key, None)
        return st

    def _iter_all_steps(self) -> Iterator[str]:
        for root in self.order:
            yield root
            stack = list(self.children.get(root, []))
            while stack:
                sid = stack.pop()
                yield sid
                stack.extend(self.children.get(sid, []))
