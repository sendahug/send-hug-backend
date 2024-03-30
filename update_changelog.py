"""
A script for updating the changelog.md file with the latest changes made to the project.

Adapted from https://github.com/PrefectHQ/prefect/pull/2529/files
"""
from collections import OrderedDict
import json
import os
from datetime import date
from glob import glob
from typing import List, TypedDict, Literal

SECTIONS = [
    "Features",
    "Changes",
    "Fixes",
    "Breaking Changes",
    "Chores",
    "Documentation",
]

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
CHANGELOG_PATH = os.path.join(REPO_DIR, "CHANGELOG.md")
CHANGES_DIR = os.path.join(REPO_DIR, "changelog")
PR_BASE_URL = os.environ.get("BASE_REPO_URL", "")


class Change(TypedDict):
    change: Literal[
        "Features", "Changes", "Fixes", "Breaking Changes", "Chores", "Documentation"
    ]
    description: str


class ChangelogEntry(TypedDict):
    pr_number: int
    changes: List[Change]


def get_formatted_changes(files: List[str]) -> OrderedDict[str, List[str]]:
    """
    Get all the changes from the changelog directory and return them sorted
    into sections by type
    """
    sorted_changes: OrderedDict[str, List[str]] = OrderedDict()

    for section in SECTIONS:
        sorted_changes[section] = []

    # Read each file in, format the changes and assign them
    # to the correct section
    for file in files:
        with open(file, "r") as f:
            changelog_entry: ChangelogEntry = json.load(f)

        if not changelog_entry["changes"] or not isinstance(
            changelog_entry["changes"], list
        ):
            raise ValueError(
                f"Invalid changelog entry in {file}. All changelog "
                "entries must have a 'changes' key that is a list of changes."
            )

        pull_request = changelog_entry["pr_number"]

        # Format each change in the entry
        for change in changelog_entry["changes"]:
            change_type = change["change"]
            pull_request_link = (
                f"([#{pull_request}]({PR_BASE_URL}/pull/{pull_request}))"
            )
            formatted_change = f"- {change['description']} {pull_request_link}\n"
            sorted_changes[change_type].append(formatted_change)

    return sorted_changes


def generate_changelog_dated_section(
    changes_to_add: OrderedDict[str, List[str]]
) -> List[str]:
    """
    Converts the changes to add into a dated section of the changelog,
    starting with the current date and with the changes split to
    their respective sections.
    Returns a list of strings that can be written to the changelog file.
    """
    current_date = date.today().strftime("%Y-%m-%d")
    sections = [f"### {current_date}\n", "\n"]

    for section_title, changes in changes_to_add.items():
        if len(changes) > 0:
            sections.extend([f"#### {section_title}\n", "\n", *changes, "\n"])

    return sections


def update_current_changelog(
    changes_to_add: OrderedDict[str, List[str]], change_files: List[str]
):
    """
    Reads the current changelog file, updates it with the new changes,
    and writes it back to the file.
    """
    # Reads in the changelog.
    with open(CHANGELOG_PATH, "r") as f:
        current_changelog = f.readlines()

    current_date = date.today().strftime("%Y-%m-%d")

    # TODO: Once we release the first version, we should remove
    # this bit and just add the date when creating a new release
    # Tries to find the current date headline
    try:
        current_date_index = current_changelog.index(f"### {current_date}\n")
    except ValueError:
        current_date_index = -1

    # If there are no entries for today, we add them at the beginning
    if current_date_index == -1:
        current_index = 4
        next_index = 5

    # Otherwise, we need to get all the existing changes for today
    # so we can overwrite the section with the previous AND the new
    # changes.
    else:
        # Grab today's section
        current_index = current_date_index + 2
        next_date = [
            line
            for line in current_changelog[current_index:]
            if line.startswith("### 20")
        ][0]
        next_index = current_changelog.index(next_date)
        existing_changes = current_changelog[current_index : next_index - 1]
        current_section = ""

        # For each line in today's section, if it's a section header,
        # we update the `current_section` so we can use it for subsequent
        # lines. Otherwise, if it's a change, we add it to the `changes_to_add`
        # with the current section as the key.
        for line in existing_changes:
            if line.startswith("#### "):
                current_section = line.split("####")[1].strip()

            if line.startswith("- "):
                changes_to_add[current_section].insert(0, line)

    # Finally, now that we have everything in order, we convert today's
    # section into a list of strings and rebuild the changelog.
    today_section = generate_changelog_dated_section(changes_to_add)
    updated_changelog = current_changelog[: current_index - 2]
    updated_changelog.extend([*today_section, *current_changelog[next_index:]])

    # Writes the updated changelog back to the file.
    with open(CHANGELOG_PATH, "w") as f:
        f.writelines(updated_changelog)

    # Deletes the changes files once they've been added to the changelog.
    for path in change_files:
        os.remove(path)


if __name__ == "__main__":
    files = glob(os.path.join(CHANGES_DIR, "*.json"))
    changes = get_formatted_changes(files=files)
    update_current_changelog(changes, change_files=files)
