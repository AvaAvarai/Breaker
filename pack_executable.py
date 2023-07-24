import cx_Freeze

executables = [cx_Freeze.Executable("main.py", icon="assets/image/ball.ico", base = "Win32GUI", target_name="breaker")]

cx_Freeze.setup(
    name="Breaker",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["assets/", "LICENSE"]}},
    executables = executables
)