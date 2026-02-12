def input_multiline(label):
    print(f"{label} (Tekan Enter 2x jika selesai):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return "\n".join(lines)
