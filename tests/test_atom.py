from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "atom"
THEMES_DIR = PROJECT_ROOT.parent

ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"
ATOM = f"{{{ATOM_NAMESPACE}}}"


@pytest.fixture(scope="module")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output_dir = tmp_path_factory.mktemp("atom-site") / "public"

    result = subprocess.run(
        [
            "hugo",
            "--source",
            str(FIXTURE_ROOT),
            "--themesDir",
            str(THEMES_DIR),
            "--destination",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Hugo failed to build the Atom fixture.\n\n"
        f"stdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )

    return output_dir


@pytest.fixture(scope="module")
def atom_feed(built_site: Path) -> ET.Element:
    atom_path = built_site / "atom.xml"

    assert atom_path.is_file(), "Hugo did not generate atom.xml"

    return ET.parse(atom_path).getroot()


def test_atom_feed_uses_atom_namespace(atom_feed: ET.Element) -> None:
    assert atom_feed.tag == f"{ATOM}feed"


@pytest.mark.parametrize("element_name", ["title", "id", "updated"])
def test_atom_feed_contains_required_metadata(
    atom_feed: ET.Element,
    element_name: str,
) -> None:
    elements = atom_feed.findall(f"{ATOM}{element_name}")

    assert len(elements) == 1
    assert elements[0].text


def test_atom_feed_title(atom_feed: ET.Element) -> None:
    assert atom_feed.findtext(f"{ATOM}title") == "Atom Test Site"


def test_atom_feed_id_is_canonical_home_url(atom_feed: ET.Element) -> None:
    assert atom_feed.findtext(f"{ATOM}id") == "https://example.org/"


def test_atom_feed_updated_uses_latest_entry_update(
    atom_feed: ET.Element,
) -> None:
    assert atom_feed.findtext(f"{ATOM}updated") == "2026-01-05T12:00:00Z"
