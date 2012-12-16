from django.contrib import messages

from django.views.generic import CreateView, UpdateView, DeleteView

#### General use objects ####
class MessageMixin(object):
    """
    Display notifications when using Class-Based Views
    """
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)


#### Generic view subclasses to add Request to Forms ####

class RequestCreateView(MessageMixin, CreateView):
    """
    Sub-class CreateView to pass Request to Form
    """
    success_message = "Created successfully"

    def get_form_kwargs(self):
        """ Add Request object to Form keyword arguments. """
        kwargs = super(RequestCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

class RequestUpdateView(MessageMixin, UpdateView):
    """
    Sub-class UpdateView to pass Request to Form and limit queryset
    to requesting user.
    """
    success_message = "Updated successfully"

    def get_form_kwargs(self):
        """ Add Request object to Form keyword arguments. """
        kwargs = super(RequestUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_queryset(self):
        """ Limit User to modifying only their own objects. """
        queryset = super(RequestUpdateView, self).get_queryset()
        return queryset.filter(owner=self.request.user)

class RequestDeleteView(MessageMixin, DeleteView):
    """
    Sub-class DeleteView to restrict User to their own data. 
    """
    success_message = "Deleted successfully"

    def get_queryset(self):
        queryset = super(RequestDeleteView, self).get_queryset()
        return queryset.filter(owner=self.request.user)
