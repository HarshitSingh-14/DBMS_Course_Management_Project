from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    from .models import Tracker
    tracker = Tracker.query.all()
    return render_template("home.html", user=current_user, tracker=tracker)


@views.route('/view-profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    return render_template("profile_page.html", user=current_user)


@views.route('/edit-profile-page', methods=['GET', 'POST'])
@login_required
def edit_profile_page():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            fullname = request.form.get('name')
            city = request.form.get('city')
            user_id = current_user.id
            current_user_email = current_user.email

            from .models import User
            user = User.query.filter_by(email=email).first()
            if user and current_user_email != email:
                flash('Email is already taken, Use Differernt email ', category='error')
            elif len(fullname) < 3:
                flash('Enter a valif name ', category='error')
            elif len(email) < 4:
                flash('Enter a valid email', category='error')
            else:
                from .models import User
                edit_user = User.query.get(user_id)

                from . import db

                edit_user.fullname = fullname
                edit_user.email = email
                edit_user.city = city

                db.session.commit()
                flash('Profile update kar diya', category='success')
                return redirect(url_for('views.view_profile'))
    except Exception as e:
        print(e)
        flash('Error Exception Refresh the database', category='error')
    return render_template("edit_profile_page.html", user=current_user)


@views.route('/add-tracker-page', methods=['GET', 'POST'])
@login_required
def add_tracker_page():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            tracker_type = request.form.get('type')
            settings = request.form.get('settings')

            from .models import Tracker
            current_user_id = current_user.id
            tracker = Tracker.query.filter_by(name=name).first()
            if tracker and current_user_id == tracker.user_id:
                flash('The comment by this name ->  "' + name + '" is already added by you .', category='error')
                return redirect(url_for('views.home'))
            else:
                from . import db
                new_tracker = Tracker(name=name, description=description, tracker_type=tracker_type, settings=settings,
                                      user_id=current_user_id)
                db.session.add(new_tracker)
                db.session.commit()
                flash('New Comment Added. Thanks for commenting !!!', category='success')
                return redirect(url_for('views.home'))
    except Exception as e:
        print(e)
        flash('#Error', category='error')
    return render_template("add_tracker_page.html", user=current_user)


@views.route('/delete-tracker/<int:record_id>', methods=['GET', 'POST'])
@login_required
def delete_tracker(record_id):
    try:
        from .models import Tracker
        Tracker_details = Tracker.query.get(record_id)
        Tracker_name = Tracker_details.name
        from . import db
        db.session.delete(Tracker_details)
        db.session.commit()
        flash(Tracker_name + ' Course removed Successfully -> Do contact us if deleted by mistake @ harshit @karuna', category='success')
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return redirect(url_for('views.home'))


@views.route('/edit-tracker/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_tracker(record_id):
    from .models import Tracker
    this_tracker = Tracker.query.get(record_id)
    this_tracker_name = this_tracker.name
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            tracker_type = request.form.get('type')
            settings = request.form.get('settings')

            current_user_id = current_user.id
            tracker = Tracker.query.filter_by(name=name).first()
            if tracker and tracker.user_id == current_user_id and this_tracker_name != name:
                flash('The Course by the name ->  "' + name + '" is already added byy u, Try a differnt name for the course of the same field',
                      category='error')
            else:
                from . import db

                this_tracker.name = name
                this_tracker.description = description
                this_tracker.tracker_type = tracker_type
                this_tracker.settings = settings

                db.session.commit()
                flash('Course Updated Successfully__', category='success')
                return redirect(url_for('views.home'))
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')

    return render_template("edit_tracker_page.html", user=current_user, tracker=this_tracker)


@views.route('/add-log-page/<int:record_id>', methods=['GET', 'POST'])
@login_required
def add_log(record_id):
    from .models import Tracker, Log
    this_tracker = Tracker.query.get(record_id)
    import datetime
    now = datetime.datetime.now()
    try:
        if request.method == 'POST':
            when = request.form.get('date')
            value = request.form.get('value')
            notes = request.form.get('notes')
            from . import db
            new_log = Log(timestamp=when, value=value, notes=notes, tracker_id=record_id, user_id=current_user.id,
                          added_date_time=now)
            db.session.add(new_log)
            db.session.commit()
            flash(' Comment added successfully  ' + this_tracker.name + ' COMMENT', category='success')
            return redirect(url_for('views.home'))
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return render_template("add_log_page.html", user=current_user, tracker=this_tracker, now=now)


@views.route('/view-tracker-graph-logs/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_tracker(record_id):
    from .models import Tracker, Log
    import datetime
    now = datetime.datetime.now()
    selected_tracker = Tracker.query.get(record_id)
    logs = Log.query.all()
    try:
        import sqlite3
        con = sqlite3.connect('E:\Quantified_Self_App\website\database.db')
        print("Database opened successfully")
        c = con.cursor()
        c.execute('SELECT timestamp, value FROM Log WHERE user_id={} AND tracker_id={}'.format(current_user.id,
                                                                                               selected_tracker.id))
        data = c.fetchall()

        dates = []
        values = []
        import matplotlib.pyplot as plt
        from matplotlib import style
        style.use('fivethirtyeight')
        from dateutil import parser

        for row in data:
            dates.append(parser.parse(row[0]))
            values.append(row[1])

        fig = plt.figure(figsize=(18, 8))
        plt.plot_date(dates, values, '-')
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        plt.tight_layout()
        plt.savefig('E:\Quantified_Self_App\website\static\Images\graph.png')
        # plt.show()

        gon = sqlite3.connect('E:\Quantified_Self_App\website\database.db')
        g = gon.cursor()
        added_date_time = g.execute('SELECT added_date_time FROM Log WHERE '
                                    'id=(SELECT max(id) FROM Log WHERE tracker_id={})'.format(record_id))

        added_date_time = added_date_time.fetchone()
        added_date_time = ''.join(added_date_time)
        print(added_date_time)
        from datetime import datetime
        last_updated = now - parser.parse(added_date_time)
        last_updated_str = str(last_updated)
        hour = last_updated_str[:1]
        min1 = last_updated_str[2]
        min2 = last_updated_str[3]
        minute = min1 + min2
        sec1 = last_updated_str[5]
        sec2 = last_updated_str[6]
        second = sec1 + sec2
        return render_template("view_tracker_logs_and_graph.html", user=current_user, tracker=selected_tracker,
                               logs=logs, hour=hour, min=minute, sec=second)
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
        return render_template("view_tracker_logs_and_graph.html", user=current_user, tracker=selected_tracker,
                               logs=logs)


@views.route('/delete-log/<int:record_id>', methods=['GET', 'POST'])
@login_required
def delete_log(record_id):
    from .models import Log
    Log_details = Log.query.get(record_id)
    tracker_id = Log_details.tracker_id
    try:
        from . import db
        db.session.delete(Log_details)
        db.session.commit()
        flash('Log Removed Successfully.', category='success')
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return redirect(url_for('views.view_tracker', record_id=tracker_id))


@views.route('/edit-log/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_log(record_id):
    from .models import Log, Tracker
    from . import db
    this_log = Log.query.get(record_id)
    this_tracker = Tracker.query.get(this_log.tracker_id)
    try:
        if request.method == 'POST':
            when = request.form.get('date')
            value = request.form.get('value')
            notes = request.form.get('notes')

            this_log.timestamp = when
            this_log.value = value
            this_log.notes = notes

            db.session.commit()
            flash(this_tracker.name + ' Log Updated Successfully.', category='success')
            return redirect(url_for('views.view_tracker', record_id=this_log.tracker_id))
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')

    return render_template("edit_log_page.html", user=current_user, tracker=this_tracker, log=this_log)
