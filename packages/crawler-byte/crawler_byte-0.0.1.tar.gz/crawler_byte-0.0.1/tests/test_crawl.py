import pytest
from pathlib import Path
from src.crawler_byte.crawler import crawl

def create_test_dir_structure(base_dir):
    # Create files and directories for testing
    (base_dir / "file1.txt").write_text("hello")
    (base_dir / "file2.txt").write_text("world")
    subdir = base_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("foo")
    subsubdir = subdir / "subsubdir"
    subsubdir.mkdir()
    (subsubdir / "file4.txt").write_text("bar")
    return {
        "files": [
            base_dir / "file1.txt",
            base_dir / "file2.txt",
            subdir / "file3.txt",
            subsubdir / "file4.txt",
        ],
        "dirs": [
            base_dir,
            subdir,
            subsubdir,
        ]
    }

def test_crawl_max_depth(tmp_path):
    structure = create_test_dir_structure(tmp_path)
    collected = []
    result = crawl(str(tmp_path), max_depth=1, action=lambda f: collected.append(f))
    # Only top-level files should be included
    expected_files = {str(tmp_path / "file1.txt"), str(tmp_path / "file2.txt")}
    result_files = {r['stats'] for r in result if r['stats'] is not None}
    assert result_files == {Path(f) for f in expected_files}
    # Directories should have stats=None
    for r in result:
        if r['stats'] is None:
            assert r['name'] in [d.name for d in structure['dirs']]
    # Callable data for files should be None (since append returns None)
    for r in result:
        if r['stats'] is not None:
            assert r['callable_data'] is None
    assert set(collected) == expected_files

def test_crawl_full_depth(tmp_path):
    structure = create_test_dir_structure(tmp_path)
    collected = []
    result = crawl(str(tmp_path), max_depth=10, action=lambda f: collected.append(f))
    expected_files = {str(f) for f in structure['files']}
    result_files = {str(r['stats']) for r in result if r['stats'] is not None}
    assert result_files == expected_files
    # Check directories are present with stats=None
    dir_names = {d.name for d in structure['dirs']}
    result_dirs = {r['name'] for r in result if r['stats'] is None}
    assert dir_names.issubset(result_dirs)
    # Callable data for files should be None
    for r in result:
        if r['stats'] is not None:
            assert r['callable_data'] is None
    assert set(collected) == expected_files

def test_crawl_os_walk(tmp_path):
    structure = create_test_dir_structure(tmp_path)
    collected = []
    result = crawl(str(tmp_path), max_depth=1001, action=lambda f: collected.append(f))
    expected_files = {str(f) for f in structure['files']}
    result_files = {str(r['stats']) for r in result if r['stats'] is not None}
    assert result_files == expected_files
    # Directories should have stats=None
    for r in result:
        if r['stats'] is None:
            assert r['name'] in [d.name for d in structure['dirs']]
    # Callable data for files should be None
    for r in result:
        if r['stats'] is not None:
            assert r['callable_data'] is None
    assert set(collected) == expected_files

def test_crawl_callable_return(tmp_path):
    (tmp_path / "file.txt").write_text("data")
    def action(path):
        return "called:" + path
    result = crawl(str(tmp_path), max_depth=1, action=action)
    file_result = [r for r in result if r['stats'] is not None][0]
    assert file_result['callable_data'].startswith("called:")
    assert file_result['stats'] == tmp_path / "file.txt"
    assert file_result['name'] == "file.txt"

def test_crawl_nonexistent_dir():
    with pytest.raises(FileNotFoundError):
        crawl("/nonexistent/path", max_depth=1, action=lambda f: None)

def test_crawl_not_a_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")
    with pytest.raises(NotADirectoryError):
        crawl(str(file_path), max_depth=1, action=lambda f: None)

def test_crawl_return_type(tmp_path):
    (tmp_path / "file.txt").write_text("data")
    result = crawl(str(tmp_path), max_depth=1, action=lambda f: None)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)

def test_crawl_empty_dir(tmp_path):
    result = crawl(str(tmp_path), max_depth=1, action=lambda f: None)
    # Should only contain the root directory entry
    assert len(result) == 1
    assert result[0]['stats'] is None
    assert result[0]['name'] == tmp_path.name

def test_crawl_symlink(tmp_path):
    (tmp_path / "file.txt").write_text("data")
    symlink = tmp_path / "link.txt"
    symlink.symlink_to(tmp_path / "file.txt")
    collected = []
    result = crawl(str(tmp_path), max_depth=2, action=lambda f: collected.append(f))
    # Should include both file.txt and link.txt
    file_names = {r['name'] for r in result if r['stats'] is not None}
    assert "file.txt" in file_names
    assert "link.txt" in file_names