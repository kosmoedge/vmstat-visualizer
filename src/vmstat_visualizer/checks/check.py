import subprocess


def check_vmstat_columns():
    try:
        command = ["vmstat", "1", "1"]
        result = subprocess.run(command,
                                capture_output=True,
                                text=True, check=True, timeout=5)
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) < 2:
            return False, False
        header_line = output_lines[1]
        has_st = "st" in header_line.split()
        has_gu = "gu" in header_line.split()
        return has_st, has_gu
    except FileNotFoundError:
        print("Error: vmstat command not found.")
        return False, False
    except subprocess.CalledProcessError as e:
        print(f"Error running vmstat: {e.stderr}")
        return False, False

