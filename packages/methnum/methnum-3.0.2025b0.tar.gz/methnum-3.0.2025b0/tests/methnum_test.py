import os
import logging
import shutil

from methnum import course
from travo.gitlab import GitLabTest, GitLab
import i18n

os.environ["LANG"] = "fr_FR.UTF-8"


def test_pipeline(assignment_name="L1/Seance1", student_group="MP1"):
    """

    Parameters
    ----------
    assignment_name
    student_group

    Examples
    --------
    >>> test_pipeline()
    """
    i18n.set("locale", "fr")
    course.log.setLevel(logging.INFO)
    course.log.info("methnum start")
    home = os.path.expanduser("~")
    course.log.info(f"{home=}")
    course.student_groups = [student_group]
    # course.subcourses = []  # remove subcourses to simplify
    course.forge = GitLabTest("http://gitlab")
    with course.forge.logged_as("instructor1"):
        course.log.info(f"after login {course.forge.get_current_user().username=}")
        course.forge.ensure_local_git_configuration(dir=os.getcwd())
        # course.forge.git(["config", "--global", "user.name", f"{course.forge.get_current_user().name}"])
        # course.forge.git(["config", "--global", "user.email", f"{course.forge.get_current_user().username}@{course.mail_extension}"])
        # course.forge.git(["config", "--global", "password", "aqwzsx(t1"])
        course.forge.git(["config", "--global", "init.defaultBranch", "master"])
        course.forge.git(["config", "--global", "pull.rebase", "false"])
        # course.deploy(share_with_instructors=False, embed=False)
        course.forge.ensure_group(path=course.path, name=course.name, visibility="public")

        # Create the subgroup for the current session
        if course.session_path is not None:
            assert course.session_name is not None
            course.forge.ensure_group(
                path=course.path + "/" + course.session_path,
                name=course.session_name,
                visibility="public",
            )
        if course.subcourses is not None:
            # Create a subgroup on the forge for each subcourse
            path = course.path
            if course.session_path is not None:
                path += "/" + course.session_path
            for subcourse in course.subcourses:
                course.forge.ensure_group(
                    path=path + "/" + subcourse,
                    name=subcourse,
                    visibility="public",
                )

        course.log.info(f"cwd: {os.getcwd()}")
        course.log.info(f"methnum generate_assignment {assignment_name}")
        course.generate_assignment(assignment_name=assignment_name)
        course.log.info(f"methnum release {assignment_name}")
        course.release(
            assignment_name=assignment_name, visibility="public", push_instructor_repo=False
        )

    # student part
    with course.forge.logged_as("student1"):
        course.forge.login(username="student1", password="aqwzsx(t1", anonymous_ok=False)
        course.log.info(f"after login {course.forge.get_current_user().username=}")
        work_dir = course.ensure_work_dir()
        course.forge.login(username="student1", password="aqwzsx(t1", anonymous_ok=False)
        course.log.info(f"after relogin {course.forge.get_current_user().username=}")
        course.log.info(f"methnum fetch {assignment_name}")
        course.fetch(assignment_name=assignment_name)
        course.log.info(f"{work_dir=}")
        assert os.path.isdir(os.path.join(work_dir))
        assert os.path.isdir(os.path.join(work_dir, assignment_name))
        assert any(
            fname.endswith(".md")
            for fname in os.listdir(os.path.join(work_dir, assignment_name))
        )
        # must run student_autograde to get .gradebook.db correct
        # go into student folder
        course.log.info(f"cwd: {os.getcwd()}")
        cwd = os.getcwd()
        course.log.info(f"os.chdir({os.path.join(work_dir, assignment_name)})")
        os.chdir(os.path.join(work_dir, assignment_name))
        course.log.info(f"cwd: {os.getcwd()}")
        course.log.info(
            f"methnum student_autograde "
            f"{os.path.basename(assignment_name)} student1.lastname"
        )
        course.student_autograde(
            assignment_name=os.path.basename(assignment_name),
            student="student1.lastname",
        )
        # go back in teacher folder
        os.chdir(cwd)
        course.log.info(f"os.chdir({cwd})")
        course.log.info(f"cwd: {os.getcwd()}")

        course.log.info(f"methnum submit {assignment_name} {student_group}")
        course.submit(assignment_name=assignment_name, student_group=student_group)

    with course.forge.logged_as("instructor1"):
        course.log.info(f"methnum collect_in_submitted {assignment_name} {student_group}")
        course.collect_in_submitted(
            assignment_name=assignment_name, student_group=student_group
        )
        shutil.move(   # adapt to nbgrader format for student names
            f'./submitted/student1/{os.path.basename(assignment_name)}',
            f'./submitted/student1.lastname/{os.path.basename(assignment_name)}'
        )
        assert os.path.isdir("./submitted")
        student_ids = os.listdir("./submitted")
        course.log.info(f"in submitted: {student_ids=}")
        assert len(student_ids) > 0
        # there is no gitlab runners to autograde the tested submission
        # so we mimic the result by copying the autograded and feedback folder
        course.log.info(f"methnum collect_autograded {assignment_name} {student_group}")
        course.collect_autograded(
            assignment_name=assignment_name, student_group=student_group
        )
        # as they are no CI in the test GitLab we can mimic the effect of collect_autograded
        # doing a copy of the submitted folder
        shutil.copytree(
            "./submitted",
            "./autograded",
            dirs_exist_ok=True,
        )
        # shutil.copytree(
        #     f'{os.path.join(home, "MethNum", assignment_name, "feedback")}',
        #     "./feedback_generated",
        #     dirs_exist_ok=True,
        # )
        shutil.copytree(
            "./submitted",
            "./feedback_generated",
            dirs_exist_ok=True,
        )
        # course.log.info(f"methnum autograde {assignment_name} {student_ids[0]}")
        # course.autograde(assignment_name=assignment_name, tag=student_ids[0])
        # course.log.info(
        #     f"methnum ensure_autograded {assignment_name} {student_group} "
        #     f"force_autograde=False"
        # )
        course.log.info(
            f"methnum merge_autograded_db {assignment_name} on_inconsistency='WARNING', "
            f"back=False, new_score_policy='greater'"
        )
        course.merge_autograded_db(
            assignment_name=os.path.basename(assignment_name),
            on_inconsistency="WARNING",
            back=False,
            new_score_policy="greater",
        )
        assert os.path.isdir("./feedback_generated")
        # course.log.info(f"methnum generate_feedback {assignment_name} {student_ids[0]}")
        # course.generate_feedback(
        #     assignment_name=assignment_name, tag=student_ids[0]
        # )
        course.log.info(f"methnum release_feedback {assignment_name} {student_group}")
        course.release_feedback(
            assignment_name=assignment_name, student_group=student_group, tag=student_ids[0]
        )


test_pipeline()
