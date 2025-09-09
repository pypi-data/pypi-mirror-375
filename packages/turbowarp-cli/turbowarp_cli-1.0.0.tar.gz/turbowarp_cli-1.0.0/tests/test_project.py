def test_project():
    from pathlib import Path

    from twcli.run import run, get_exit_code

    __file_path__ = Path(__file__).resolve()
    proj_path = (__file_path__ / '..' / '..' / "Project.sb3").resolve()

    assert proj_path.exists()
    project_data = proj_path.read_bytes()

    assert get_exit_code(run(project_data, [
        "faretek",
        "yes",
        "no"
    ])) == '0'  # 0

    assert get_exit_code(run(project_data, [
        "faretek",
        "yes",
        "yes"
    ])) == '1'  # 1

    assert get_exit_code(run(project_data, [
        "faretek",
        "no"
    ])) == '1'  # 1
