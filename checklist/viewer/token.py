class Token(object):
    def __init__(self, default: str, tag: str, version: int, display_tag: str, is_lock: bool=False):
        self.default = default
        self.tag = tag
        self.version = version
        self.display_tag = self.compute_display_tag()
        self.is_lock = is_lock or tag == ""
    
    def is_abstract(self):
        return self.tag and self.tag != ""
    
    def is_general_mask(self):
        return self.tag == "mask"
    
    def compute_display_tag(self, use_bracelet: bool=False) -> str:
        if not self.is_abstract():
            return ""
        else:
            tag_version = f"{self.tag}{self.version}"
            if use_bracelet:
                tag_version = f"[{tag_version}]" if self.is_general_mask() else "{" + tag_version + "}"
            return tag_version
    
    def compile(self, use_default: bool):
        if use_default or self.is_lock:
            return self.default
        else:
            return f"[{self.tag}]"
    
    def serialize(self):
        return (self.default, self.display_tag)

    def __repr__(self):
        return f'"{self.default}{self.display_tag}"'