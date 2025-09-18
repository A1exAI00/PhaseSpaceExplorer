from typing import Protocol, List, Callable, Dict, Tuple

class DSLoader(Protocol):
    @property
    def folderpath(self):
        raise NotImplementedError
    
    @property
    def filepath(self):
        raise NotImplementedError

    @property
    def variable_names(self) -> List[str]:
        raise NotImplementedError
    
    @property
    def parameter_names(self) -> List[str]:
        raise NotImplementedError
    
    @property
    def ODEs(self) -> Callable:
        raise NotImplementedError
    
    @property
    def periodic_data(self) -> Dict[int, Tuple[float, float]]:
        raise NotImplementedError

    @property
    def periodic_events(self) -> List[Callable]:
        raise NotImplementedError