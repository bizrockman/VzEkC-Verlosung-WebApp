import io
import sys

from django.shortcuts import render

from utils.VzEkC import VzEkC, test_lottery


def home(request):
    context = {}

    if request.GET.get('reset'):
        request.session.flush()

    # Step 1
    set_nr_of_packages(request)

    # Step 2
    set_packages(request)

    # Step 3
    set_players(request)

    if request.session.get('packages') and request.session.get('packages').get('1') and \
            request.session.get('packages').get('1').get('players') and request.POST.get('start'):
        test_lottery()

        drawings = []
        for packageNr, package in request.session.get('packages').items():
            names = []
            for player in package.get('players'):
                for lose in range(int(player['nrLose'])):
                    names.append(player['name'])
            drawings.append({'text': packageNr+' - '+package.get('name'), 'names': names})

        if not request.POST.get('seed'):
            post_timestamp = '12334556'
        else:
            post_timestamp = request.POST.get('seed')

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        lottery = VzEkC(drawings, post_timestamp)
        lottery.print_drawing()

        message = new_stdout.getvalue()

        sys.stdout = old_stdout

        context.update({'lottery_message': message})

    return render(request, 'templates/home.html', context)


def set_players(request):
    session = request.session

    if session.get('packages') and session.get('packages').get('1') and \
        not session.get('packages').get('1').get('players') and request.POST.get('namePlayer1Package1'):
        packages = session.get('packages')
        for packageNr, package in packages.items():

            for player in range(1, int(package.get('nrOfPlayers')) + 1):
                if 'players' not in package:
                    package['players'] = []
                player_name = request.POST.get('namePlayer' + str(player) + 'Package' + packageNr)
                nr_lose = request.POST.get('nrLosePlayer' + str(player) + 'Package' + packageNr)
                package['players'].append({'id': player, 'name': player_name, 'nrLose': nr_lose})
                request.session.modified = True


def set_packages(request):
    packages = {}
    session = request.session

    if session.get('nrOfPackages') and not session.get('packages') and request.POST.get('nameOfPackage1'):
        for package_nr in range(1, int(session.get('nrOfPackages'))+1):
            packages[package_nr] = {'id': package_nr,
                                    'name': request.POST.get('nameOfPackage'+str(package_nr)),
                                    'nrOfPlayers': str(request.POST.get('nrOfPlayersOfPackage'+str(package_nr)))}
        session['packages'] = packages


def set_nr_of_packages(request):
    if request.POST.get('nrOfPackages'):
        request.session['nrOfPackages'] = request.POST.get('nrOfPackages')
