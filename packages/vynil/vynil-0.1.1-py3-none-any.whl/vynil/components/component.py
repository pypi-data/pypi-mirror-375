from __future__ import annotations
import pathlib
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Iterable

from auryn import GX

if TYPE_CHECKING:
    from ..formats import Render

ROOT = pathlib.Path(__file__).parent
BUILTIN_COMPONENTS_DIRECTORY = ROOT / "builtins"
GX.add_plugins_directory(ROOT / "plugins")

type ComponentArgument = str | pathlib.Path | dict[str, Any] | Component


class Component:
    """
    A component available in a book's rendering.

    Attributes:
        name: The component name.
        text: The component text.
        path: The component path.
    """

    # Conventions:
    on_load_name: ClassVar[str] = "on_load"
    main_name: ClassVar[str] = "render"
    GLOBALS: ClassVar[str] = "globals"
    CONTENT: ClassVar[str] = "content"

    def __init__(
        self,
        name: str,
        text: str,
        path: pathlib.Path | None = None,
    ) -> None:
        self.name = name
        self.text = text
        self.path = path

    def __str__(self) -> str:
        return f"component {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def resolve(cls, component: ComponentArgument) -> Component:
        """
        Resolve a component.

        Arguments:
            component: The component to resolve.
                If it's a component object, it's returned as-is; if it's a string or path object, it's loaded from that
                file; if it's a dictionary, it's converted to a component object.

        Returns:
            The resolved component.
        """
        if isinstance(component, Component):
            return component
        if isinstance(component, dict):
            return cls(**component)
        path = pathlib.Path(component)
        text = path.read_text()
        return cls(
            name=path.name.split(".")[0],
            text=text,
            path=path,
        )
    
    @classmethod
    def builtins(cls) -> Iterable[Component]:
        """
        Return the built-in components.

        Returns:
            An iterable of built-in components.
        """
        for path in BUILTIN_COMPONENTS_DIRECTORY.glob("*"):
            if path.is_dir():
                continue
            yield cls.resolve(path)
    
    def load(self, render: Render) -> dict[str, Any]:
        context: dict[str, Any] = {}
        if self.path.suffix == ".py":
            module: dict[str, Any] = {}
            code = compile(self.text, str(self.path or self.name), "exec")
            exec(code, module)
            on_load = getattr(module, self.on_load_name, None)
            if on_load is not None:
                on_load(render)
            main = getattr(module, self.main_name, None)
            if main is not None:
                context[f"{GX.generation_prefix}{self.name}"] = main
            for name, value in module.items():
                if name.startswith((GX.generation_prefix, GX.execution_prefix)):
                    context[name] = value
        else:
            template = self.path or self.text
            context[f"{GX.generation_prefix}{self.name}"] = self._create_component(template)
        return context

    def _create_component(self, template: str | pathlib.Path) -> Callable[[GX, Any], None]:
        def g_component(gx: GX, arg: str | None = None, **kwargs: Any) -> None:
            gx.state[self.CONTENT] = gx.line.children
            component_gx = gx.derive(template, continue_generation=True)
            component_gx.template.lines.snap(gx.line.indent)
            component_gx.generate()
            globals_: list[Any] = gx.state.setdefault(self.GLOBALS, [])
            globals_.append({"arg": arg, **kwargs})
            gx.add_code("globals_before = globals().copy()")
            gx.add_code(f"globals().update(get({len(globals_) - 1}))")
            gx.extend(component_gx)
            gx.add_code("restore_globals(globals_before, globals())")
            gx.state.pop(self.CONTENT, None)

        return g_component