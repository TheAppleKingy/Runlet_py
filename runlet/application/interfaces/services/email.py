from typing import Protocol


class EmailMessageTextTemplate:
    """
    Class returns templates of topic and message text to send mails
    """
    @classmethod
    def notify_student_subscribed(cls, course_name: str, url: str):
        return "Subscribed on course!", f"You have successfully subscribed on course '{course_name}'. Start learning right now on Runlet\n{url}"

    @classmethod
    def notify_student_requested_subscribe(self, course_name: str, url: str):
        return "Request for subscribe on course!", f"You have successfully requested for subscribe on course '{course_name}'. Until you waiting see more courses and start learning on Runlet!\n{url}"

    @classmethod
    def notify_teacher_requested_subscribe(cls, requestor: str, course_name: str, url: str):
        return "Request for subscribe on your course!", f"{requestor} wants to subscribe on your course '{course_name}'. Accept or reject request on Runlet\n{url}"

    @classmethod
    def registration(self, confirm_url: str):
        return "Registration confirm", f"Hello! Confirm your registration on Runlet following by link:\n{confirm_url}"

    @classmethod
    def change_password(self, confirm_url: str):
        return "Change password", f"You requested changing of the password on Runlet. Follow the link\n{confirm_url}"

    @classmethod
    def rate_student(self, problem_name: str, url: str):
        return "Attempt rated", f"Attempt for problem '{problem_name}' was rated. See result on Runlet\n{url}"

    @classmethod
    def notify_student_unsubscribed(self, course_name: str, url: str):
        return "Unsubscribed from course!", f"You unsubscribed from course '{course_name}'. Start learning right now on other courses on Runlet\n{url}"

    @classmethod
    def notify_student_was_expelled(self, course_name: str, url: str):
        return "Expelled from course", f"You were expelled from course '{course_name}'. See on Runlet\n{url}"


class EmailServiceInterface(Protocol):
    async def send_mail(self, to: str, topic: str, text: str): ...
