from typing import Protocol


class EmailMessageTextTemplate:
    """
    Class returns templates of topic and message text to send mails
    """
    @classmethod
    def notify_student_subscribed(cls, course_name: str):
        return "Subscribed on course!", f"You have successfully subscribed on course '{course_name}'. Start learning right now on Runlet\n"

    @classmethod
    def notify_student_requested_subscribe(self, course_name: str):
        return "Request for subscribe on course!", f"You have successfully requested for subscribe on course '{course_name}'. Until you waiting see more courses and start learning on Runlet!\n"

    @classmethod
    def notify_teacher_requested_subscribe(cls, requestor: str, course_name: str):
        return "Request for subscribe on your course!", f"{requestor} wants to subscribe on your course '{course_name}'. Accept or reject request on Runlet\n"

    @classmethod
    def registration(self, confirm_url: str):
        return "Registration confirm", f"Hello! Confirm your registration on Runlet following by link:\n{confirm_url}"


class EmailServiceInterface(Protocol):
    async def send_mail(self, to: str, topic: str, text: str): ...
