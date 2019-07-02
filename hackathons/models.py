from django.db import models

from companies.models import Company
from contacts.models import Contact

class Hackathon(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(blank=True)
    fundraising_goal = models.IntegerField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def latest():
        return Hackathon.objects.latest("date")


class Tier(models.Model):
    name = models.CharField(max_length=100)

    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="tiers"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Perk(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="perks"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sponsorship(models.Model):
    CONTACTED = "contacted"
    RESPONDED = "responded"
    CONFIRMED = "confirmed"
    DENIED = "denied"
    GHOSTED = "ghosted"
    PAID = "paid"
    STATUSES = (
        (CONTACTED, "Contacted"),
        (RESPONDED, "Responded"),
        (CONFIRMED, "Confirmed"),
        (DENIED, "Denied"),
        (GHOSTED, "Ghosted"),
        (PAID, "Paid"),
    )

    hackathon = models.ForeignKey(
        Hackathon, on_delete=models.CASCADE, related_name="sponsorships"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sponsorships"
    )
    contribution = models.IntegerField(blank=True, default=0)
    status = models.CharField(max_length=20, choices=STATUSES, default=CONTACTED)
    tier = models.ForeignKey(Tier, related_name="sponsorships", on_delete=models.SET_NULL, null=True)
    perks = models.ManyToManyField(Perk, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hackathon', 'company',)

    def __str__(self):
        return f"Company: {self.company}, Status: {self.status}, Contribution: {self.contribution}"

class Lead(models.Model):
    CONTACTED = "contacted"
    RESPONDED = "responded"
    STATUSES = ((CONTACTED, "Contacted"), (RESPONDED, "Responded"))
    NO_ROLE = "no_role"
    PRIMARY = "primary"
    ROLES = ((NO_ROLE, "None"), (PRIMARY, "Primary"))

    sponsorship = models.ForeignKey(
        Sponsorship, on_delete=models.CASCADE, related_name="leads"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="leads"
    )

    status = models.CharField(max_length=20, choices=STATUSES)
    role = models.CharField(max_length=20, choices=ROLES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sponsorship', 'contact',)

    def status_pretty(self):
        return dict(self.STATUSES)[self.status]

    def role_pretty(self):
        return dict(self.ROLES)[self.role]

    def __str__(self):
        return f"Sponsorship: {self.sponsorship}, Contact: {self.contact}, Status: {self.status}, Role: {self.role}"
