import re
import sys
import matplotlib.pyplot as plt

def parse_vmstat(lines):
    data = {
        'time': [],
        'r': [], 'b': [],
        'swpd': [], 'free': [], 'inact': [], 'active': [],
        'si': [], 'so': [],
        'bi': [], 'bo': [],
        'us': [], 'sy': [], 'id': [], 'wa': [], 'st': [], 'gu': []
    }
    time0 = None
    for line in lines:
        # Skip header lines
        if re.match(r'\s*r\s+b\s+', line) or '--procs--' in line or '--' in line or 'EEST' in line or 'timestamp' in line:
            continue
        fields = line.strip().split()
        # Expect at least 18 columns + timestamp
        if len(fields) < 18:
            continue
        try:
            # Parse fields
            r, b = int(fields[0]), int(fields[1])
            swpd, free, inact, active = map(int, fields[2:6])
            si, so = int(fields[6]), int(fields[7])
            bi, bo = int(fields[8]), int(fields[9])
            us, sy, idl, wa, st, gu = map(int, fields[12:18])
            timestamp = fields[-2] if ':' in fields[-2] else fields[-1]
        except Exception:
            continue
        # Calculate seconds since first sample
        if time0 is None:
            time0 = timestamp
            sec = 0
        else:
            # Just increment by 1 for each line (since vmstat interval is 1s)
            sec = len(data['time'])
        data['time'].append(sec)
        data['r'].append(r)
        data['b'].append(b)
        data['swpd'].append(swpd)
        data['free'].append(free)
        data['inact'].append(inact)
        data['active'].append(active)
        data['si'].append(si)
        data['so'].append(so)
        data['bi'].append(bi)
        data['bo'].append(bo)
        data['us'].append(us)
        data['sy'].append(sy)
        data['id'].append(idl)
        data['wa'].append(wa)
        data['st'].append(st)
        data['gu'].append(gu)
    return data

def plot_vmstat(data):
    t = data['time']

    # 1. System Load
    plt.figure(figsize=(10,4))
    plt.plot(t, data['r'], label='Running (r)')
    plt.plot(t, data['b'], label='Blocked (b)')
    plt.title('System Load')
    plt.xlabel('Seconds')
    plt.ylabel('Processes')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vmstat_system_load.png')
    plt.close()

    # 2. Memory Usage
    plt.figure(figsize=(10,4))
    plt.plot(t, data['free'], label='Free')
    plt.plot(t, data['inact'], label='Inactive')
    plt.plot(t, data['active'], label='Active')
    plt.plot(t, data['swpd'], label='Swap Used')
    plt.title('Memory Usage')
    plt.xlabel('Seconds')
    plt.ylabel('Memory (units as in input)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vmstat_memory.png')
    plt.close()

    # 3. CPU Usage
    plt.figure(figsize=(10,4))
    plt.plot(t, data['us'], label='User')
    plt.plot(t, data['sy'], label='System')
    plt.plot(t, data['id'], label='Idle')
    plt.plot(t, data['wa'], label='Wait')
    plt.plot(t, data['st'], label='Steal')
    plt.title('CPU Usage (%)')
    plt.xlabel('Seconds')
    plt.ylabel('Percent')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vmstat_cpu.png')
    plt.close()

    # 4. Swap
    plt.figure(figsize=(10,4))
    plt.plot(t, data['swpd'], label='Swap Used')
    plt.plot(t, data['si'], label='Swap In')
    plt.plot(t, data['so'], label='Swap Out')
    plt.title('Swap Usage')
    plt.xlabel('Seconds')
    plt.ylabel('Swap (units as in input)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vmstat_swap.png')
    plt.close()

    # 5. IO
    plt.figure(figsize=(10,4))
    plt.plot(t, data['bi'], label='Blocks In')
    plt.plot(t, data['bo'], label='Blocks Out')
    plt.title('IO')
    plt.xlabel('Seconds')
    plt.ylabel('Blocks')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vmstat_io.png')
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vmstat_plot.py <vmstat.log>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    data = parse_vmstat(lines)
    plot_vmstat(data)
    print("Charts saved as vmstat_*.png")
