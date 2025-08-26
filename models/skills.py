class Skills:
    def __init__(self, crp=0, crafting=None, tool_proficiencies=None, languages=None):
        self.crp = crp
        self.crafting = crafting or []
        self.tool_proficiencies = tool_proficiencies or []
        self.languages = languages or []

    def get_summary(self) -> str:
        return f"**Crafting Reputation:** {self.crp}"
