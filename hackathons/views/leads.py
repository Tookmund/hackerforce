from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Hackathon, Sponsorship, Lead
from companies.models import Company
from contacts.models import Contact
from ..forms import HackathonForm, LeadForm


def leads_show(request, h_pk):
    hackathon = get_object_or_404(Hackathon, pk=h_pk)

    def state_filter(states):
        return Lead.objects.filter(sponsorship__hackathon=hackathon, status__in=states)

    def paginator_wrapper(name, obj):
        order_by = request.GET.get(f"{name}_order_by")
        if order_by:
            obj = obj.order_by(order_by)
        paginator = Paginator(obj, 25)
        return paginator.get_page(request.GET.get(f"{name}_page"))
    
    def get_q(name):
        return request.GET["q"] if request.GET.get("q") else request.GET.get(f"{name}_q")
    
    def lead_wrapper(name, states):
        obj = state_filter(states)
        q = get_q(name)
        if q:
            obj = obj.filter(Q(contact__first_name__icontains=q) | Q(contact__last_name__icontains=q) | Q(contact__company__name__icontains=q) | Q(contact__company__industries__name__iexact=q))
        return paginator_wrapper(name, obj.distinct())
    
    def contact_wrapper(name):
        contacts_for_hackathon = Contact.objects.filter(leads__sponsorship__hackathon__pk=h_pk).values_list("pk", flat=True)
        obj = Contact.objects.exclude(pk__in=contacts_for_hackathon)
        q = get_q(name)
        if q:
            obj = obj.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(company__name__icontains=q))
        return paginator_wrapper(name, fake_leads(obj.distinct()))

    def fake_leads(contacts):
        return [Lead(pk=0, contact=c, sponsorship=Sponsorship(pk=0, company=c.company)) for c in contacts]

    responded = lead_wrapper("responded", [Lead.RESPONDED])
    contacted = lead_wrapper("contacted", [Lead.CONTACTED])
    uncontacted = contact_wrapper("uncontacted")
    dead = lead_wrapper("dead", [Lead.GHOSTED])

    return render(request, "leads_show.html", {
        "responded": responded,
        "contacted": contacted,
        "uncontacted": uncontacted,
        "dead": dead,
    })


def lead_new(request, h_pk):
    if request.method == "POST":
        form = LeadForm(request.hackathon, None, request.POST)
        if form.is_valid():
            lead = form.save(commit=True)
            lead.save()
            return redirect("hackathons:leads:view", h_pk=h_pk, pk=lead.contact.pk)
    else:
        contact_pk = request.GET.get("contact")
        contact = get_object_or_404(Contact, pk=contact_pk) if contact_pk else None
        sponsorship = None
        company = None
        if contact:
            sponsorship = Sponsorship.objects.filter(hackathon__pk=h_pk, company__pk=contact.company.pk)
            sponsorship = sponsorship[0] if sponsorship else None
            company = get_object_or_404(Company, pk=contact.company.pk)
            if not sponsorship:
                messages.info(request, f"Before you can create a lead for {contact}, you need to begin tracking {company}. Press save below and then navigate back to the contact page.")
                return redirect(reverse("hackathons:sponsorships:new", args=(h_pk,)) + "?company=" + str(company.pk))
        
        initial = {
            "contact": contact if contact_pk else None,
            "sponsorship": sponsorship if company_pk else None,
        }
        form = LeadForm(request.hackathon, company, initial=initial)
    return render(request, "lead_new.html", {"form": form})

def lead_edit(request, h_pk, pk):
    lead = get_object_or_404(Lead, sponsorship__hackathon__pk=h_pk, contact__pk=pk)
    if request.method == "POST":
        form = LeadForm(request.hackathon, lead.sponsorship.company, request.POST, instance=lead)
        if form.is_valid():
            lead = form.save(commit=True)
            lead.save()
            return redirect("hackathons:leads:view", h_pk=h_pk, pk=lead.contact.pk)
    else:
        form = LeadForm(request.hackathon, lead.sponsorship.company, instance=lead)
    return render(request, "lead_edit.html", {"form": form})

def lead_detail(request, h_pk, pk):
    contact = get_object_or_404(Contact, pk=pk)

    lead = Lead.objects.filter(sponsorship__hackathon__pk=h_pk, contact__pk=pk)
    lead = lead[0] if lead else None

    sponsorship = Sponsorship.objects.filter(hackathon__pk=h_pk, company__pk=contact.company.pk)
    sponsorship = sponsorship[0] if sponsorship else None

    lead_contacts = sponsorship.leads.all().values_list('contact__id', flat=True) if sponsorship else []
    non_lead_contacts = set(contact.company.contacts.all().values_list('id', flat=True)) - set(lead_contacts)

    contacts = [{"lead": lead, "contact": lead.contact} for lead in Lead.objects.filter(contact__id__in=lead_contacts)]
    contacts += [{"contact": contact} for contact in Contact.objects.filter(id__in=non_lead_contacts)]

    return render(request, "lead_detail.html", {
        "lead": lead,
        "contact": contact,
        "sponsorship": sponsorship,
        "contacts": contacts
    })
