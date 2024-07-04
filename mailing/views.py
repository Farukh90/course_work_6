from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Client, Message, Mailing, MailingAttempt

class ClientListView(ListView):
    model = Client
    template_name = 'mailing/client_list.html'


class ClientDetailView(DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'


class ClientCreateView(CreateView):
    model = Client
    template_name = 'mailing/client_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailing:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'mailing/client_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailing:client_list')


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')


class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'


class MessageCreateView(CreateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:client_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')



class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'


class MailingCreateView(CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['description', 'start_time', 'actual_end_time', 'periodicity', 'message', 'clients']
    success_url = reverse_lazy('mailing:mailing_list')


class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['description', 'start_time', 'actual_end_time', 'periodicity', 'message', 'clients']
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        mailing_id = self.kwargs['mailing_id']
        return MailingAttempt.objects.filter(mailing_id=mailing_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_id'] = self.kwargs['mailing_id']
        return context


class MailingAttemptDetailView(DetailView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_detail.html'


class MailingAttemptCreateView(CreateView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_form.html'
    fields = []

    def get_initial(self):
        initial = super().get_initial()
        initial['mailing_id'] = self.kwargs['mailing_id']
        return initial

    def form_valid(self, form):
        form.instance.mailing_id = self.kwargs['mailing_id']
        return super().form_valid(form)

    def get_success_url(self):
        mailing_id = self.kwargs['mailing_id']
        return reverse_lazy('mailing:mailing_attempt_list', kwargs={'mailing_id': mailing_id})


class MailingAttemptUpdateView(UpdateView):
    model = MailingAttempt
    fields = ['status', 'server_response']
    template_name = 'mailing/mailing_attempt_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_id'] = self.object.mailing.id
        return context

    def get_success_url(self):
        return reverse('mailing:mailing_attempt_list', kwargs={'mailing_id': self.object.mailing.id})


class MailingAttemptDeleteView(DeleteView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


# Представление для запуска рассылки
def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.start_mailing()
    return redirect('mailing:mailing_detail', pk=pk)


# Представление для завершения рассылки
def complete_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.complete_mailing()
    return redirect('mailing:mailing_detail', pk=pk)



def create_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})

def update_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})

def delete_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})
