class Item:
    def __init__(self, name="", description="", benefits="", link=""):
        self.name = name
        self.description = description
        self.benefits = benefits
        self.link = link

    def get_summary(self) -> str:
        return (f"**Item:** {self.name}\n"
                f"**Description:** {self.description}\n"
                f"**Benefits:** {self.benefits}\n"
                f"**Link:** {self.link}")
