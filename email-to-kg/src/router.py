"""
Content router for writing to knowledge graph files.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class ContentRouter:
    """Routes classified emails to appropriate markdown files."""

    def __init__(self, personal_dir: Path):
        self.personal_dir = Path(personal_dir)
        self.work_file = self.personal_dir / "work.md"
        self.personal_file = self.personal_dir / "personal.md"
        self.home_file = self.personal_dir / "home.md"
        self.people_dir = self.personal_dir / "people"
        self.logs_dir = self.personal_dir / "logs"
        self.knowledge_dir = self.personal_dir / "knowledge" / "references"

        # Ensure directories exist
        self.people_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

    def route(self, email, classification) -> list[str]:
        """
        Route email content to appropriate files.
        Returns list of files modified.
        """
        modified_files = []

        category = classification.category

        if category == "ignore":
            return []

        if category == "work_task":
            self._add_to_work(email, classification)
            modified_files.append(str(self.work_file))

        elif category == "personal_task":
            self._add_to_personal(email, classification)
            modified_files.append(str(self.personal_file))

        elif category == "home_task":
            self._add_to_home(email, classification)
            modified_files.append(str(self.home_file))

        elif category == "person_info":
            files = self._add_to_people(email, classification)
            modified_files.extend(files)

        elif category == "knowledge":
            file = self._add_to_knowledge(email, classification)
            if file:
                modified_files.append(file)

        elif category == "log_entry":
            file = self._add_to_daily_log(email, classification)
            modified_files.append(file)

        # Also add people interactions if people mentioned
        if classification.people and category != "person_info":
            self._add_people_interactions(email, classification)

        return modified_files

    def _format_task_line(self, classification) -> str:
        """Format a task line for TODO sections."""
        parts = [f"- [{classification.priority}]", classification.summary]

        if classification.deadline:
            parts.append(f"@deadline:{classification.deadline}")

        for person in classification.people[:2]:  # Limit to 2 people
            parts.append(f"@person:{person}")

        if "waiting" in classification.tags:
            parts.append("@waiting")
        if "followup" in classification.tags:
            parts.append("@followup")

        return " ".join(parts)

    def _insert_into_section(
        self,
        file_path: Path,
        section_header: str,
        content: str,
        create_section: bool = True
    ) -> None:
        """Insert content under a section header in a markdown file."""
        file_path = Path(file_path)

        if not file_path.exists():
            # Create file with section
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"# {file_path.stem.title()}\n\n{section_header}\n{content}\n")
            return

        text = file_path.read_text()
        lines = text.split('\n')

        # Find section
        section_idx = None
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                section_idx = i
                break

        if section_idx is not None:
            # Insert after section header
            lines.insert(section_idx + 1, content)
        elif create_section:
            # Add section at end
            lines.append("")
            lines.append(section_header)
            lines.append(content)

        file_path.write_text('\n'.join(lines))

    def _add_to_work(self, email, classification) -> None:
        """Add task to work.md TODO section."""
        task_line = self._format_task_line(classification)
        self._insert_into_section(self.work_file, "## TODO", task_line)

    def _add_to_personal(self, email, classification) -> None:
        """Add task to personal.md TODO section."""
        task_line = self._format_task_line(classification)
        self._insert_into_section(self.personal_file, "## TODO", task_line)

    def _add_to_home(self, email, classification) -> None:
        """Add task to home.md TODO section."""
        task_line = self._format_task_line(classification)
        self._insert_into_section(self.home_file, "## TODO", task_line)

    def _add_to_people(self, email, classification) -> list[str]:
        """Add person info to people files."""
        modified = []

        for person in classification.people:
            # Create safe filename
            safe_name = re.sub(r'[^\w\s-]', '', person.lower())
            safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
            person_file = self.people_dir / f"{safe_name}.md"

            date_str = email.date.strftime("%Y-%m-%d")
            interaction = f"- {date_str}: {classification.summary} (via email)"

            self._insert_into_section(person_file, "## Interactions", interaction)
            modified.append(str(person_file))

        return modified

    def _add_people_interactions(self, email, classification) -> None:
        """Add interaction entries for mentioned people."""
        date_str = email.date.strftime("%Y-%m-%d")

        for person in classification.people:
            safe_name = re.sub(r'[^\w\s-]', '', person.lower())
            safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
            person_file = self.people_dir / f"{safe_name}.md"

            interaction = f"- {date_str}: Email regarding: {classification.summary}"
            self._insert_into_section(person_file, "## Interactions", interaction)

    def _add_to_knowledge(self, email, classification) -> Optional[str]:
        """Add knowledge entry."""
        # Extract topic from summary
        summary = classification.summary
        safe_topic = re.sub(r'[^\w\s-]', '', summary[:50].lower())
        safe_topic = re.sub(r'[-\s]+', '-', safe_topic).strip('-')

        if not safe_topic:
            safe_topic = "misc"

        knowledge_file = self.knowledge_dir / f"{safe_topic}.md"

        date_str = email.date.strftime("%Y-%m-%d")
        content = f"""
## {classification.summary}

*Source: Email from {email.from_addr} on {date_str}*

{email.body[:1000]}

---
"""

        if knowledge_file.exists():
            existing = knowledge_file.read_text()
            knowledge_file.write_text(existing + content)
        else:
            knowledge_file.write_text(f"# {summary}\n{content}")

        return str(knowledge_file)

    def _add_to_daily_log(self, email, classification) -> str:
        """Add entry to daily log."""
        date_str = email.date.strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{date_str}.md"

        from_name = email.from_addr.split('<')[0].strip() or email.from_addr
        entry = f"- **Email from {from_name}**: {classification.summary}"

        if classification.action_items:
            entry += "\n" + "\n".join(f"  - [ ] {item}" for item in classification.action_items)

        self._insert_into_section(log_file, "## Email Activity", entry)

        return str(log_file)
