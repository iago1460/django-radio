import datetime
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render, get_list_or_404
from django.utils.translation import ugettext_lazy as _

from radio.apps.dashboard.forms import ProgrammeForm, ProgrammeMinimumForm, UserProfileForm, UserForm, RoleForm, RoleMinimumForm
from radio.apps.programmes.models import Programme, Role
from radio.apps.schedules.models import Schedule
from radio.apps.users.models import UserProfile


def __get_context_permissions(request):
    user = request.user
    return {'display_schedule_editor': schedule_permissions(user), 'display_settings':False,
            'display_programme_list':user.has_perm('programmes.change_programme'),
            'display_role_list':user.has_perm('programmes.change_role')}

@login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', dict(context.items() + __get_context_permissions(request).items()))

@login_required
@permission_required('programmes.change_programme', raise_exception=False)
def programme_list(request):
    context = {'programme_list': Programme.objects.all().order_by('-start_date')}
    return render(request, 'dashboard/programme_list.html', dict(context.items() + __get_context_permissions(request).items()))

@login_required
@permission_required('programmes.change_programme', raise_exception=False)
def edit_programme(request, slug):
    user = request.user
    programme = get_object_or_404(Programme, slug=slug)
    form = ProgrammeForm(instance=programme)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, request.FILES, instance=programme)
        if form.is_valid():
            form.save()
            return redirect('dashboard:programme_list')
    context = {'form': form}
    return render(request, "dashboard/edit_programme.html", dict(context.items() + __get_context_permissions(request).items()))

@login_required
@permission_required('programmes.add_programme', raise_exception=False)
def create_programme(request):
    user = request.user
    if request.method == 'GET':
        form = ProgrammeForm()
    else:
        form = ProgrammeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard:programme_list')
    context = {'form': form}
    return render(request, "dashboard/edit_programme.html", dict(context.items() + __get_context_permissions(request).items()))



@login_required
@permission_required('programmes.change_role', raise_exception=False)
def role_list(request):
    context = {'role_list': Role.objects.all().order_by('-person').select_related('programme')}
    return render(request, 'dashboard/role_list.html', dict(context.items() + __get_context_permissions(request).items()))


@login_required
@permission_required('programmes.change_role', raise_exception=False)
def edit_role(request, id):
    role = get_object_or_404(Role.objects.select_related('programme'), id=id)
    form = RoleForm(instance=role)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('dashboard:role_list')
    context = {'form': form, 'programme_name' : role.programme.name}
    return render(request, "dashboard/edit_role.html", dict(context.items() + __get_context_permissions(request).items()))

@login_required
@permission_required('programmes.add_role', raise_exception=False)
def create_role(request):
    if request.method == 'GET':
        form = RoleForm()
    else:
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:role_list')
    context = {'form': form}
    return render(request, "dashboard/edit_role.html", dict(context.items() + __get_context_permissions(request).items()))



@login_required
def my_programme_list(request):
    context = {'programme_list': Programme.objects.filter(announcers__in=[request.user]).distinct()}
    return render(request, 'dashboard/my_programme_list.html', dict(context.items() + __get_context_permissions(request).items()))



@login_required
def my_role_list(request):
    context = {'role_list': Role.objects.filter(person=request.user).order_by('-programme').select_related('programme')}
    return render(request, 'dashboard/my_role_list.html', dict(context.items() + __get_context_permissions(request).items()))

def check_edit_role_permissions(user):
    return user.has_perm('programmes.change_role') or user.has_perm('programmes.change_his_role')

@login_required
@user_passes_test(check_edit_role_permissions)
def edit_my_role(request, id):
    user = request.user
    role = get_object_or_404(Role.objects.select_related('programme'), id=id, person=user)
    form = RoleMinimumForm(instance=role)
    if request.method == 'POST':
        form = RoleMinimumForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('dashboard:my_role_list')
    context = {'form': form, 'programme_name' : role.programme.name}
    return render(request, "dashboard/edit_role.html", dict(context.items() + __get_context_permissions(request).items()))

def check_edit_programme_permissions(user):
    return user.has_perm('programmes.change_programme') or user.has_perm('programmes.change_his_programme')

@login_required
@user_passes_test(check_edit_programme_permissions)
def edit_my_programme(request, slug):
    user = request.user
    programme = get_object_or_404(Programme, slug=slug)
    if not (user in programme.announcers.all()):
        raise Http404
    form = ProgrammeMinimumForm(instance=programme)
    if request.method == 'POST':
        form = ProgrammeMinimumForm(request.POST, request.FILES, instance=programme)
        if form.is_valid():
            form.save()
            return redirect('dashboard:my_programme_list')
    context = {'form': form}
    return render(request, "dashboard/edit_programme.html", dict(context.items() + __get_context_permissions(request).items()))





@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    pform = UserProfileForm(instance=profile)
    uform = UserForm(instance=user)
    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        pform = UserProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()
            profile = pform.save()
            # profile = pform.save(commit=False)
            # profile.user = user
            # profile.save()
            return redirect('dashboard:index')
    context = {'uform':uform, 'pform':pform}
    return render(request, 'dashboard/edit_profile.html', dict(context.items() + __get_context_permissions(request).items()))


# FullCalendar
def ajax_view(f):
    """Return a valid ajax response"""
    def vista(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_ajax():
            return HttpResponseBadRequest()
        try:
            res = f(request, *args, **kwargs)
            error = None
        except ValidationError, e:
            res = None
            error = json.dumps('; '.join(e.messages))
        except Exception, e:
            res = None
            if settings.DEBUG:
                error = json.dumps(str('; '.join(e.messages)))
            else:
                error = str("Internal error")

        return HttpResponse(
            json.dumps({
                'error': error,
                'response': res
            }),
            content_type='application/json; charset=utf8'
        )
    return vista

def schedule_permissions(user):
    """
    for x in user.get_all_permissions():
        print x
    """
    return user.has_perm('schedules.add_schedule') and user.has_perm('schedules.change_schedule') and user.has_perm('schedules.delete_schedule')


@user_passes_test(schedule_permissions)
@login_required
def full_calendar(request):
    context = {'event_url':'all_events/'}
    return render(request, 'dashboard/fullcalendar.html', dict(context.items() + __get_context_permissions(request).items()))

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def change_event(request):
    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    id = int(request.POST.get('id'))
    schedule = get_object_or_404(Schedule, id=id)
    now = datetime.datetime.now().date()
    if (schedule.programme.end_date is not None and start.date() >= schedule.programme.end_date) or start.date() < schedule.programme.start_date or start.date() < now:
        raise ValidationError(_('Out of programme date range'))
    schedule.start_hour = start.time()
    schedule.day = start.weekday()
    schedule.clean()
    schedule.save()

background_colours = { "L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA" }
text_colours = { "L": "black", "B": "black", "S": "black" }

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def create_schedule(request):
    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    id = int(request.POST.get('programmeId'))
    type = request.POST.get('type')
    programme = get_object_or_404(Programme, id=id)
    now = datetime.datetime.now().date()
    if (programme.end_date is not None and start.date() >= programme.end_date) or start.date() < programme.start_date or start.date() < now:
        raise ValidationError(_('Out of programme date range'))
    schedule = Schedule(programme=programme, day=start.weekday(), start_hour=start.time(), type=type)
    schedule.clean()
    schedule.save()
    return {'scheduleId': schedule.id, 'backgroundColor':background_colours[schedule.type], 'textColor':text_colours[schedule.type]}

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def delete_schedule(request):
    id = int(request.POST.get('scheduleId'))
    schedule = get_object_or_404(Schedule, id=id)
    schedule.delete()

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def programmes(request):
    programmes = Programme.actives(datetime.datetime.now().date())
    response_data = []
    for programme in programmes:
        response_data.append({'title' : programme.name, 'runtime' : programme._runtime, 'programmeId' : programme.id})
    return response_data

@login_required
@user_passes_test(schedule_permissions)
def all_events(request):
    if not settings.DEBUG and not request.is_ajax():
        return HttpResponseBadRequest()

    start = datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
    end = datetime.datetime.strptime(request.GET.get('end'), '%Y-%m-%d')

    # Don't show past schedules
    now = datetime.datetime.now().date()
    if start.date() < now:
        start = datetime.datetime.combine(now, datetime.time(0, 0, 0))
    else:
        start = datetime.datetime.combine(start.date(), datetime.time(0, 0, 0))

    end = datetime.datetime.combine(end.date(), datetime.time(23, 59, 59))

    json_list = []
    if end >= start:
        schedules, dates = Schedule.between(start, end)
        for x in range(len(schedules)):
            schedule = schedules[x]
            for y in range(len(dates[x])):
                date = dates[x][y]
                # start = date.strftime("%Y-%m-%dT%H:%M:%S"+utc_str)
                json_entry = {'id':schedule.id, 'start':str(date), 'end':str(date + schedule.runtime()),
                              'allDay':False, 'title': schedule.programme.name, 'textColor':text_colours[schedule.type] , 'backgroundColor':background_colours[schedule.type]}
                json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')

