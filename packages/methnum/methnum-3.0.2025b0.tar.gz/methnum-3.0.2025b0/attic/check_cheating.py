#!/usr/bin/python3.6
import os


script = os.getenv("COURSE_SCRIPT")


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_ownership(log):
    owners = []
    submitters = []
    f = open(log, 'r')
    suspicion = False
    for line in f:
        if "own" in line and "CollectApp" not in line:
            split = line.split(' by ')
            submitter = split[1].split(' ')[0]
            owner = split[2].split(' ')[0][:-1]
            if '--' in submitter:
                submitter = submitter.split('--')[0]
            if submitter.count('.') == 2:
                submitter = submitter.split('.')[1]+"."+submitter.split('.')[2]
            submitters.append(submitter)
            owners.append(owner)
            if '.' in submitter:
                firstname, lastname = submitter.split('.')
                if "." not in owner:  # short login
                    if firstname[0] != owner[0]:
                        print(
                            f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Owner is {owner} and "
                            f"submitter is {submitter} (suspicion of different first names).{Colors.ENDC}")
                        suspicion = True
                    if owner[1:-2] not in lastname:
                        print(
                            f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Owner is {owner} and "
                            f"submitter is {submitter} (suspicion of different last names).{Colors.ENDC} ")
                        suspicion = True
                else:
                    if owner[1:-2] not in submitter:
                        print(
                            f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Owner is {owner} and "
                            f"submitter is {submitter} (suspicion of different last names).{Colors.ENDC} ")
                        suspicion = True                    
            elif owner != submitter:
                if owner != "unknow":
                    print(f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Owner is {owner} and "
                          f"submitter is {submitter}.{Colors.ENDC}")
                    suspicion = True
    multiple_owners = []
    for owner in owners:
        c = owners.count(owner)
        if c > 1 and owner not in multiple_owners:
            multiple_owners.append(owner)
            multiple_submitters = [submitters[k] for k, o in enumerate(owners) if o == owner]
            print(f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Owner {owner} have {c} submissions under "
                  f"the submitter names {multiple_submitters}!  Possible multiple submissions "
                  f"of the same evaluation from the same owner with different submitter names.{Colors.ENDC}")
            suspicion = True
    return suspicion


def check_machine_id(log):
    machine_ids = []
    submitters = []
    f = open(log, 'r')
    suspicion = False
    # check if most of the files have been submitted with submit-exam
    n_exams = 0
    count = 0
    for line in f:
        if "[CollectApp | INFO] Collecting submission" in line or \
                "[CollectApp | INFO] Submission already exists" in line:
            n_exams += 1
            submitter = line.split(": ")[1].split(" ")[0]
            if '--' in submitter:
                count += 1
    f.close()
    print(f"[{script} | INFO] {Colors.OKGREEN}{count}/{n_exams} submissions have been "
          f"submitted with submit-exam and a machine ID.{Colors.ENDC}")
    if count > 0.8 * n_exams:
        print("Check for machine IDs...")
        if count != n_exams:
            print(f"[{script} | WARNING] {Colors.WARNING}Anonymity problem? Not all evaluations have been "
                  f"submitted with submit-exam. Exam rules may have not been followed by all students.{Colors.ENDC}")
        f = open(log, 'r')
        for line in f:
            if "[CollectApp | INFO] Collecting submission" in line or \
                    "[CollectApp | INFO] Submission already exists" in line:
                full_submitter = line.split(": ")[1].split(' ')[0]
                if '--' in full_submitter:
                    submitter, machine_id = full_submitter.split('--')
                    submitters.append(submitter)
                    machine_ids.append(machine_id)
                else:
                    suspicion = True
                    print(f"[{script} | WARNING] {Colors.WARNING}Anonymity problem? Submitter {full_submitter} "
                          f"has no machine ID and so have not submitted his evaluation using submit-exam. "
                          f"Possible break of the anonymity. Check the notebook file.{Colors.ENDC}")
        f.close()
        multiple_machine_ids = []
        for machine_id in machine_ids:
            c = machine_ids.count(machine_id)
            if c > 1 and machine_id not in multiple_machine_ids:
                multiple_machine_ids.append(machine_id)
                multiple_submitters = [submitters[k] for k, m in enumerate(machine_ids) if m == machine_id]
                print(
                    f"[{script} | WARNING] {Colors.WARNING}Cheating attempt? Machine ID {machine_id} "
                    f"have {c} submissions under the submitter names {multiple_submitters}! Possible multiple "
                    f"submissions of the same evaluation from the same machine with different submitter names.{Colors.ENDC}")
                suspicion = True
    else:
        print(f"[{script} | INFO] {Colors.OKGREEN}Less than 80% of the evaluations have been submitted "
              f"with a machine ID.{Colors.ENDC}")
        print(f"[{script} | INFO] {Colors.OKGREEN}If students have submitted their evaluations with 'methnum submit' "
              f"this is normal.{Colors.ENDC}")
        print(f"[{script} | INFO] {Colors.OKGREEN}If the exam rule was to use 'methnum submit-exam', "
              f"then something very bad happened for the anonymity of the evaluation.{Colors.ENDC}")
    return suspicion


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument(dest="input", default=["./submitted/collect.log"],
                        help="Input log file name. It can be a list separated by spaces, or it can use * as wildcard.",
                        nargs='*')
    args = parser.parse_args()

    for logfile in args.input:
        susp = check_ownership(logfile)
        susp += check_machine_id(logfile)
        if not susp:
            print(f"[{script} | INFO] {Colors.OKGREEN}No cheating attempt on ownership is detected.{Colors.ENDC}")
