from django.db import models
from authentication.models import User
import PyPDF2
import textract
import os

# generate a alphanumeric 9 caracters long code
def generate_interview_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    parsed_resume = models.TextField(null=True, blank=True)

    interview_code = models.CharField(max_length=255, default=generate_interview_code)

    job_title = models.CharField(max_length=255, null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    
    INTERVIEW_TYPE = (
        ('HR', 'HR'),
        ('Technical', 'Technical'),
        ('Managerial', 'Managerial'),
    )
    interview_type = models.CharField(max_length=255, choices=INTERVIEW_TYPE, null=True, blank=True)
    INTERVIEW_STATUS = (
        ('Scheduled', 'Scheduled'),
        ('Rescheduled', 'Rescheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    interview_status = models.CharField(max_length=255, choices=INTERVIEW_STATUS, default='Scheduled')
    interview_date = models.DateTimeField(null=True, blank=True)

    feedback = models.TextField(null=True, blank=True)
    feedback_rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def parse_resume(self, resume):
        # if resume is a PDF
        if resume.name.endswith('.pdf'):
            pdfReader = PyPDF2.PdfReader(resume)
            text = ''
            for page in range(len(pdfReader.pages)):
                text += pdfReader.pages[page].extract_text()
            return text

        # if resume is a DOCX
        elif resume.name.endswith('.docx'):
            text = textract.process(resume)
            return text.decode('utf-8')

        # if resume is a DOC
        elif resume.name.endswith('.doc'):
            text = textract.process(resume)
            return text.decode('utf-8')

        return None

    def __str__(self):
        return self.user.email
    
    class Meta:
        ordering = ['-created_at']

class InterviewConversation(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)

    question = models.TextField()
    response = models.TextField()
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.interview.user.email

    class Meta:
        ordering = ['-created_at']
