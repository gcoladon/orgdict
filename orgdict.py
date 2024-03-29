#
# A few functions for loading org mode files up into a nested python dictionary for
# easy manipulation via python utility programs for doing things like converting
# addresses from a spreadsheet to roam nodes, and from roam nodes to address labels,
# and from roam node addresses to family members for storiing birthdays, and
# from roam node addresses to lat long locstions.
#

# the keys at each level are title, prologue, properties, content, and sections, in that order.
def dump(j, ast = 1):
    result_lines = []
    if 'title' in j:
        result_lines.append(j['title'])
    if 'prologue' in j:
        result_lines.append(j['prologue'])
    if 'properties' in j:
        result_lines.append(":PROPERTIES:")
        for k, v in j['properties'].items():
            result_lines.append(f":{k}: {v}")
        result_lines.append(":END:")
    if 'content' in j:
        result_lines.append("\n".join(j['content']))
    if 'sections' in j:
        for sec in j['sections']:
            result_lines.append("*" * ast + " " + dump(sec, ast + 1))
    return "\n".join(result_lines)

def load(text, ast = 1, starting_line = 0):
    this_section = {"line": starting_line}
    raw_splits = text.split("\n" + "*" * ast + " ")
    # import pdb; pdb.set_trace()
    first_split_lines = raw_splits[0].split("\n")

    if ast > 1:
        this_section['title'] = first_split_lines[0]
        first_split_lines = first_split_lines[1:]

    prologue = []

    if len(first_split_lines) > 0:
        if ":PROPERTIES:" in first_split_lines:
            while first_split_lines[0] != ":PROPERTIES:":
                prologue.append(first_split_lines[0])
                first_split_lines = first_split_lines[1:]

            properties = {}
            first_split_lines = first_split_lines[1:]
            while first_split_lines[0] != ":END:":
                # I needed to add this to deal with a blank line in a properties drawer!
                if first_split_lines[0] == "":
                    first_split_lines = first_split_lines[1:]
                    continue
                # print ("{" + first_split_lines[0] + "}")
                try:
                    k, v = first_split_lines[0][1:].split(": ", maxsplit=1)
                except:
                    k, v = first_split_lines[0][1:].split(":", maxsplit=1)
                properties[k] = v
                first_split_lines = first_split_lines[1:]
            first_split_lines = first_split_lines[1:]
            this_section['properties'] = properties

    while len(first_split_lines) > 0 and ("SCHEDULED" in first_split_lines[0] or "DEADLINE" in first_split_lines[0]):
        prologue.append(first_split_lines[0])
        first_split_lines = first_split_lines[1:]
    if prologue != []:
        this_section['prologue'] = "\n".join(prologue)

    if len(first_split_lines) > 0:
        this_section['content'] = first_split_lines

    if len(raw_splits[1:]) > 0:
        lens = [len(spl.split("\n")) for spl in raw_splits]
        idxes = []
        for i in range(len(lens)):
            if i == 0:
                if ast == 1:
                    idxes.append(lens[0] + 1)
                else:
                    idxes.append(lens[0])
            else:
                idxes.append(idxes[-1] + lens[i])
        this_section['sections'] = [load(spl, ast+1, starting_line + l) for spl, l in zip(raw_splits[1:], idxes)]

    return this_section


def section_title_dict(section_array):
    std = {}
    for section in section_array:
        if 'title' in section:
            std[section['title']] = section
    return (std)

def section_title_list(section_array):
    stl = []
    for section in section_array:
        if 'title' in section:
            stl.append(section['title'])
    return (stl)


def read(filename):
    return load(open(filename, "r").read().rstrip())

def write(filename, js):
    open(filename, "w").write(dump(js) + "\n")


import subprocess

def all_person_nodes():
    return subprocess.run(["grep -il '#+filetags: person' ~/org/roam/*/*.org"],
                          capture_output=True, shell=True).stdout.decode().rstrip().split("\n")

def all_roam_nodes_match(regexp):
    return subprocess.run([f"ls ~/org/roam/*/{regexp}*.org"],
                          capture_output=True, shell=True).stdout.decode().rstrip().split("\n")

def all_roam_nodes():
    return subprocess.run([f"ls ~/org/roam/*/*.org"],
                          capture_output=True, shell=True).stdout.decode().rstrip().split("\n")
