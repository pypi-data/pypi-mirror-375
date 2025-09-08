from typing import Callable
import pytest
from pathlib import Path
import subprocess

from lando_cli.cli import (
    Config,
    get_new_commits,
    get_commit_patches,
    get_commit_message,
    detect_new_tags,
    detect_merge_from_current_head,
    determine_base_sha_for_push,
    get_current_branch,
)


@pytest.mark.parametrize(
    "config_content, expected, should_raise",
    [
        (
            """
            [auth]
            api_token = "fake_token"
            user_email = "test@example.com"
            lando_url = "https://lando.test"
            """,
            {
                "api_token": "fake_token",
                "user_email": "test@example.com",
                "lando_url": "https://lando.test",
            },
            False,
        ),
        (
            """
            [auth]
            api_token = "fake_token"
            user_email = "test@example.com"
            """,
            {
                "api_token": "fake_token",
                "user_email": "test@example.com",
                "lando_url": "https://lando.moz.tools",
            },
            False,
        ),
        (
            """
            [auth]
            user_email = "test@example.com"
            """,
            {},
            True,
        ),
        (
            """
            [auth]
            api_token = "fake_token"
            """,
            {},
            True,
        ),
    ],
)
def test_config_loading_parametrized(
    tmp_path: Path, monkeypatch, config_content, expected, should_raise
):
    config_file = tmp_path / "lando.toml"
    config_file.write_text(config_content)

    monkeypatch.setenv("LANDO_CONFIG_PATH", str(config_file))

    if should_raise:
        with pytest.raises(KeyError):
            Config.load_config()
    else:
        config = Config.load_config()
        assert (
            config.api_token == expected["api_token"]
        ), "API token does not match value in config."
        assert (
            config.user_email == expected["user_email"]
        ), "User email does not match value in config."
        assert (
            config.lando_url == expected["lando_url"]
        ), "Lando URL does not match value in config."


def test_get_current_branch(git_local_repo: Path):
    subprocess.run(["git", "switch", "-c", "testbranch"], cwd=git_local_repo)
    branch = get_current_branch(git_local_repo)
    assert branch == "testbranch"


def test_get_new_commits(git_local_repo: Path, create_commit: Callable):
    # Create a new commit
    create_commit()

    commits = get_new_commits("main", "origin/main", git_local_repo)
    assert len(commits) == 1

    commit_message = get_commit_message(commits[0], git_local_repo)
    assert commit_message.strip() == "New commit"


@pytest.mark.parametrize("patch_content", [b"patch content", b"patch\r\ncontent"])
def test_get_commit_patches(
    git_local_repo: Path, create_commit: Callable, patch_content: bytes
):
    commit_message = "Patch commit"
    create_commit(patch_content, commit_message)
    commits = get_new_commits("main", "origin/main", git_local_repo)
    patches = get_commit_patches(commits, git_local_repo)

    assert len(patches) == 1
    assert patches[0].find(commit_message.encode("utf-8"))
    assert patches[0].find(patch_content)


def test_detect_new_tags(git_local_repo: Path):
    subprocess.run(["git", "tag", "v1.0"], cwd=git_local_repo)

    new_tags = detect_new_tags(git_local_repo)
    assert "v1.0" in new_tags

    # Push tag to remote
    subprocess.run(["git", "push", "--tags"], cwd=git_local_repo)

    new_tags_after_push = detect_new_tags(git_local_repo)
    assert not new_tags_after_push


def test_detect_merge_from_current_head_true_merge(
    git_local_repo: Path, create_commit: Callable
):
    # Create a branch and commit
    subprocess.run(["git", "switch", "-c", "branch"], cwd=git_local_repo)
    create_commit("branch content", "Branch commit")

    # Switch to main and merge with no-ff
    subprocess.run(["git", "switch", "main"], cwd=git_local_repo)
    subprocess.run(
        ["git", "merge", "--no-ff", "branch", "-m", "Merge branch"], cwd=git_local_repo
    )

    actions = detect_merge_from_current_head(git_local_repo)
    assert actions is not None
    assert len(actions) == 1
    assert actions[0]["commit_message"] == "Merge branch"
    assert actions[0]["action"] == "merge-onto"
    assert actions[0]["target"] is not None


def test_detect_merge_from_current_head_fast_forward(
    git_local_repo: Path, create_commit: Callable
):
    commit_message = "FF commit"

    subprocess.run(["git", "switch", "-c", "ff-branch"], cwd=git_local_repo)
    create_commit("ff content", commit_message, "ff_file.txt")

    # Switch to main and perform fast-forward merge
    subprocess.run(["git", "switch", "main"], cwd=git_local_repo)
    subprocess.run(["git", "merge", "ff-branch"], cwd=git_local_repo)

    actions = detect_merge_from_current_head(git_local_repo)
    assert actions is not None
    assert len(actions) == 1
    assert actions[0]["commit_message"] == commit_message
    assert actions[0]["target"] is not None


def test_determine_base_sha_for_push_no_relbranch(git_local_repo: Path):
    """Test determine_base_sha_for_push without a relbranch."""
    base_sha, relbranch_specifier = determine_base_sha_for_push(
        git_local_repo,
        push_branch="main",
        default_remote_branch="main",
        relbranch=None,
    )
    assert base_sha == "origin/main"
    assert relbranch_specifier is None


def test_determine_base_sha_for_push_with_relbranch_existing(git_local_repo: Path):
    """Test determine_base_sha_for_push with existing relbranch."""
    # Create and push a relbranch
    subprocess.run(["git", "switch", "-c", "FIREFOX_100_RELBRANCH"], cwd=git_local_repo)
    subprocess.run(
        ["git", "push", "-u", "origin", "FIREFOX_100_RELBRANCH"], cwd=git_local_repo
    )

    base_sha, relbranch_specifier = determine_base_sha_for_push(
        git_local_repo,
        push_branch="FIREFOX_100_RELBRANCH",
        default_remote_branch="main",
        relbranch="FIREFOX_100_RELBRANCH",
    )
    assert base_sha == "origin/FIREFOX_100_RELBRANCH"
    assert relbranch_specifier == {"branch_name": "FIREFOX_100_RELBRANCH"}


def test_determine_base_sha_for_push_with_relbranch_missing(
    git_local_repo: Path, create_commit: Callable
):
    """Test determine_base_sha_for_push with a missing relbranch."""
    # Make sure we're on a different branch and make a commit
    subprocess.run(["git", "switch", "-c", "feature"], cwd=git_local_repo)
    create_commit("feature work", "Feature commit", "newfile.txt")

    base_sha, relbranch_specifier = determine_base_sha_for_push(
        git_local_repo,
        push_branch="feature",
        default_remote_branch="main",
        relbranch="FIREFOX_101_RELBRANCH",
    )

    # Should be the result of `git merge-base feature origin/main`
    merge_base = subprocess.run(
        ["git", "merge-base", "feature", "origin/main"],
        cwd=git_local_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert base_sha == merge_base
    assert relbranch_specifier == {
        "branch_name": "FIREFOX_101_RELBRANCH",
        "commit_sha": merge_base,
    }
