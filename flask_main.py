import warnings
import numpy, csv, os, uuid, app, dot_env
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
from app.handler.csv_main import init_csv_files
from app.handler.data_formatting import word_new_line_tag_html_safe
from app.handler.notification import send_contact_email
from app.ml.ml_model import symptom_set

warnings.filterwarnings("ignore")
'''
Defined Routes:  

'/'                     :    Home Page
'/prediction/new'       :    Creating a new Prediction Form Page
'/prediction/history'   :    All the history of Predictions made by user.
'/results'              :    Result for New Prediction Form after ML Submission Page
'/about-us'             :    About Us Page
'/contact'              :    Creating the Contact us - Query Page

'/'

'/queries/all'          :    Admin Console - For viewing All Queries Page

'''

flask_app = Flask(__name__, static_folder='static')
flask_app.secret_key = 'your-secret-key-change-this-in-production'
flask_app.config['PERMANENT_SESSION_LIFETIME'] = 86400
flask_app.config['DEBUG'] = True


@flask_app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template(
        'index.html',
        appname =dot_env.HTML_APP_TITLE,
        ver=dot_env.APP_VERSION,
        updatedOn=dot_env.UPDATED_ON,
        username=session.get('username'),
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE,
        email= app.handler.csv_main.get_user_by_username(session.get('username'))['email']
    )

@flask_app.route('/prediction/new')
def index_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template(
        'index_form.html',
        appname =dot_env.HTML_APP_TITLE,
        ver=dot_env.APP_VERSION,
        updatedOn=dot_env.UPDATED_ON,
        symptoms=symptom_set,
        username=session.get('username'),
        email= app.handler.csv_main.get_user_by_username(session.get('username'))['email'],
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
    )

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        print(f"Login attempt for username: '{username}'")

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template(
                'login.html',
                appname =dot_env.HTML_APP_TITLE
            )

        user = app.handler.csv_main.get_user_by_username(username)
        print(f"User found: {user is not None}")

        if user:
            print(f"Checking password for user: {user['username']}")
            if check_password_hash(user['password_hash'], password):
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                # session.permanent = True
                flash(f'Welcome back, {user["username"]}!', 'success')
                print(f"Login successful for: {username}")
                return redirect(url_for('index'))
            else:
                print("Password check failed")
                flash('Invalid password. Please try again.', 'error')
        else:
            print("User not found")
            flash('Username not found. Please check your username or register for a new account.', 'error')

    return render_template(
        'login.html',
        appname=dot_env.HTML_APP_TITLE
    )

@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        print(f"Registration attempt for: {username}, {email}")

        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address', 'error')
            return render_template('register.html',
        appname =dot_env.HTML_APP_TITLE)

        if app.handler.csv_main.get_user_by_username(username):
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        if app.handler.csv_main.email_exists(email):
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template(
                'register.html',
                appname =dot_env.HTML_APP_TITLE
            )

        user_id = app.handler.csv_main.create_user(username, email, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            # session.permanent = True
            flash(f'Account created successfully! Welcome, {username}!', 'success')
            print(f"Registration successful for: {username}")
            return redirect(url_for('index'))
        else:
            flash('Registration failed. Please try again.', 'error')

    return render_template(
        'register.html',
        appname =dot_env.HTML_APP_TITLE
    )

@flask_app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@flask_app.route('/prediction/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    symptoms_ = [request.form.get(f'Symptom{each_number}', '') for each_number in range(1, 18)]
    value_top_n_result = int(request.form.get('TopN', 5))
    symptoms_text = [word.strip().replace(" ", "_").lower() for word in symptoms_ if word.strip()]

    list_of_user_symptoms_2 = [0] * len(app.ml.ml_model.feature)

    for intervals in range(len(app.ml.ml_model.feature)):
        for each_symptom in symptoms_text:
            if each_symptom.lower() == app.ml.ml_model.feature[intervals]:
                list_of_user_symptoms_2[intervals] = 1

    input_user = [list_of_user_symptoms_2]
    predict_proba = app.ml.ml_model.clf3.predict_proba(input_user)[0]

    top5_diseases_default = ["No sufficient symptoms provided"] * value_top_n_result

    top_indices = numpy.argsort(predict_proba)[::-1][:value_top_n_result]
    top_diseases = [app.ml.ml_model.disease[top] for top in top_indices]

    if not any(symptoms_text):
        top_diseases = top5_diseases_default

    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%d/%m/%Y at %I:%M:%S %p")
    symptoms_str = ', '.join([s for s in symptoms_text if s])
    diseases_str = ', '.join(top_diseases)

    with open(dot_env.DB_STORAGE_PREDICTION, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            prediction_id, session['user_id'], session['username'],
            symptoms_str, diseases_str, value_top_n_result, timestamp
        ])

    return render_template(
        'result.html',
        appname =dot_env.HTML_APP_TITLE,
        ver=dot_env.APP_VERSION,
        updatedOn=dot_env.UPDATED_ON,
        topvalue=value_top_n_result,
        top_diseases=top_diseases,
        symptoms=symptoms_text,
        username=session.get('username'),
        email= app.handler.csv_main.get_user_by_username(session.get('username'))['email'],
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
    )

@flask_app.route('/prediction/history')
def my_predictions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_predictions = []
    try:
        with open(dot_env.DB_STORAGE_PREDICTION, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['user_id'] == session['user_id']:
                    user_predictions.append({
                        'symptoms': row['symptoms'].split(', ') if row['symptoms'] else [],
                        'diseases': row['predicted_diseases'].split(', ') if row['predicted_diseases'] else [],
                        'top_n': row['top_n'],
                        'timestamp': row['timestamp']
                    })
    except FileNotFoundError:
        pass

    user_predictions.reverse()
    return render_template(
        'mypredictions.html',
        appname =dot_env.HTML_APP_TITLE,
        ver=dot_env.APP_VERSION,
        updatedOn=dot_env.UPDATED_ON,
        predictions=user_predictions,
        username=session.get('username'),
        email= app.handler.csv_main.get_user_by_username(session.get('username'))['email'],
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
    )


@flask_app.route('/clear_predictions', methods=['POST'])
def clear_predictions():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    try:
        all_predictions = []
        user_predictions_count = 0

        try:
            with open(dot_env.DB_STORAGE_PREDICTION, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['user_id'] != session['user_id']:
                        all_predictions.append(row)
                    else:
                        user_predictions_count += 1
        except FileNotFoundError:
            return jsonify({'success': True, 'message': 'No predictions found to clear'})

        with open(dot_env.DB_STORAGE_PREDICTION, 'w', newline='') as file:
            if all_predictions:
                fieldnames = [
                    'prediction_id', 'user_id', 'username', 'symptoms',
                    'predicted_diseases', 'top_n', 'timestamp'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_predictions)

        return jsonify({
            'success': True,
            'message': f'Successfully cleared {user_predictions_count} predictions',
            'deleted_count': user_predictions_count
        })

    except Exception as e:
        print(f"Error clearing predictions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear predictions'
        }), 500


@flask_app.route('/clear_predictions/<username>', methods=['POST'])
def clear_predictions_by_username(username):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    try:
        target_user = app.handler.csv_main.get_user_by_username(username)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        target_user_id = target_user.get('user_id')

        all_predictions = []
        deleted_count = 0

        try:
            with open(dot_env.DB_STORAGE_PREDICTION, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] != username and row['user_id'] != target_user_id:
                        all_predictions.append(row)
                    else:
                        deleted_count += 1
        except FileNotFoundError:
            return jsonify({
                'success': True,
                'message': 'No predictions found to clear'
            })

        with open(dot_env.DB_STORAGE_PREDICTION, 'w', newline='') as file:
            if all_predictions:
                fieldnames = [
                    'prediction_id', 'user_id', 'username', 'symptoms',
                    'predicted_diseases', 'top_n', 'timestamp'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_predictions)

        return jsonify({
            'success': True,
            'message': f'Successfully cleared {deleted_count} predictions for user {username}',
            'deleted_count': deleted_count
        })

    except Exception as e:
        print(f"Error clearing predictions for {username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear predictions'
        }), 500


@flask_app.route('/delete/this/prediction', methods=['POST'])
def delete_this_prediction():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': 'User not logged in'
        }), 401

    try:
        request_data = request.get_json()
        if not request_data or 'timestamp' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Timestamp not provided'
            }), 400

        target_timestamp = request_data['timestamp']
        current_user_id = session['user_id']

        all_predictions = []
        prediction_found = False
        prediction_deleted = None

        try:
            with open(dot_env.DB_STORAGE_PREDICTION, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    if (row['user_id'] == current_user_id and
                            row['timestamp'] == target_timestamp):
                        prediction_found = True
                        prediction_deleted = row
                    else:
                        all_predictions.append(row)

        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'No predictions file found'
            }), 404

        if not prediction_found:
            return jsonify({
                'success': False,
                'error': 'Prediction not found or access denied'
            }), 404

        with open(dot_env.DB_STORAGE_PREDICTION, 'w', newline='') as file:
            if all_predictions:
                fieldnames = [
                    'prediction_id', 'user_id', 'username', 'symptoms',
                    'predicted_diseases', 'top_n', 'timestamp'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_predictions)

        return jsonify({
            'success': True,
            'message': 'Prediction deleted successfully',
            'deleted_prediction': {
                'timestamp': prediction_deleted['timestamp'],
                'symptoms': prediction_deleted['symptoms'],
                'diseases': prediction_deleted['predicted_diseases']
            }
        })

    except Exception as e:
        print(f"Error deleting prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete prediction'
        }), 500


@flask_app.route('/delete/this/prediction/<prediction_id>', methods=['DELETE'])
def delete_prediction_by_id(prediction_id):
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': 'User not logged in'
        }), 401

    try:
        current_user_id = session['user_id']

        all_predictions = []
        prediction_found = False
        prediction_deleted = None

        try:
            with open(dot_env.DB_STORAGE_PREDICTION, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if (row['prediction_id'] == prediction_id and
                            row['user_id'] == current_user_id):
                        prediction_found = True
                        prediction_deleted = row
                    else:
                        all_predictions.append(row)

        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'No predictions file found'
            }), 404

        if not prediction_found:
            return jsonify({
                'success': False,
                'error': 'Prediction not found or access denied'
            }), 404

        with open(dot_env.DB_STORAGE_PREDICTION, 'w', newline='') as file:
            if all_predictions:
                fieldnames = [
                    'prediction_id', 'user_id', 'username', 'symptoms',
                    'predicted_diseases', 'top_n', 'timestamp'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_predictions)

        return jsonify({
            'success': True,
            'message': 'Prediction deleted successfully',
            'deleted_prediction': {
                'prediction_id': prediction_deleted['prediction_id'],
                'timestamp': prediction_deleted['timestamp']
            }
        })

    except Exception as e:
        print(f"Error deleting prediction {prediction_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete prediction'
        }), 500

@flask_app.route('/about-us')
def about():
    print(app.handler.csv_main.get_user_by_username(session.get('username'))['email'])
    return render_template(
        'about.html',
        appname =dot_env.HTML_APP_TITLE,
        ver=dot_env.APP_VERSION,
        updatedOn=dot_env.UPDATED_ON,
        username=session.get('username'),
        email= app.handler.csv_main.get_user_by_username(session.get('username'))['email'],
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
    )

@flask_app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(
        flask_app.static_folder,
        filename
    )


@flask_app.route('/contact')
def contact():
    return render_template(
        'contact.html',
        appname =dot_env.HTML_APP_TITLE,
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
    )


@flask_app.route('/contact/submit', methods=['POST'])
def contact_submit():
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        contact_type = request.form.get('contact_type', '').strip()
        subject = request.form.get('subject', '').strip()
        query = request.form.get('query', '').strip()
        priority = request.form.get('priority', 'low')
        subscribe = request.form.get('subscribe', 'no')

        if not all([name, email, contact_type, query]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('contact'))

        timestamp = datetime.now().strftime("%d/%m/%Y at %I:%M:%S %p")
        csv_data = {
            'timestamp': timestamp,
            'name': name,
            'email': email,
            'contact_type': contact_type,
            'subject': subject or f"{contact_type.title()} Inquiry",
            'query': query,
            'priority': priority,
            'subscribe': subscribe,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }

        csv_file = dot_env.DB_STORAGE_QUERY
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            fieldnames = [
                'timestamp', 'name', 'email', 'contact_type', 'subject',
                'query', 'priority', 'subscribe', 'user_agent', 'ip_address'
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(csv_data)

        if csv_data['priority'] == 'high':
            try:
                send_contact_email(csv_data)
            except Exception as e:
                print(f"Email sending failed: {e}")

        flash(f'Thank you, {name}! Your message has been sent successfully. We\'ll get back to you within 24-48 hours.',
              'success')
        return redirect(url_for('contact'))

    except Exception as e:
        print(f"Contact form error: {e}")
        flash('Sorry, there was an error processing your request. Please try again.', 'error')
        return redirect(url_for('contact'))


@flask_app.route('/queries/all')
def view_all_queries():
    try:
        queries = []
        if os.path.exists(dot_env.DB_STORAGE_QUERY):
            with open(dot_env.DB_STORAGE_QUERY, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                queries = list(reader)
                print(f"Successfully read {len(queries)} queries from CSV")

                queries.reverse()
                for each_query in queries:
                    each_query['query'] = word_new_line_tag_html_safe(each_query['query'])

        return render_template(
            'queries.html',
            appname =dot_env.HTML_APP_TITLE,
            ver=dot_env.APP_VERSION,
            updatedOn=dot_env.UPDATED_ON,
            queries=queries,
            username=session.get('username'),
            passwordAdmin=dot_env.ADMIN_PASSWORD,
            email=app.handler.csv_main.get_user_by_username(session.get('username'))['email'],
        support_email=dot_env.SUPPORT_EMAIL,
        support_phone=dot_env.SUPPORT_PHONE
        )
    except Exception:
        flash('Error loading queries.', 'error')
        return redirect(url_for('index'))


@flask_app.route('/queries/delete', methods=['POST'])
def delete_query():
    timestamp = request.json.get('timestamp')

    try:
        queries = []
        if os.path.exists(dot_env.DB_STORAGE_QUERY):
            with open(dot_env.DB_STORAGE_QUERY, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                queries = [row for row in reader if row['timestamp'] != timestamp]

        if queries:
            fieldnames = queries[0].keys()
            with open(dot_env.DB_STORAGE_QUERY, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(queries)
        else:
            with open(dot_env.DB_STORAGE_QUERY, 'w', newline='', encoding='utf-8') as file:
                fieldnames = [
                    'timestamp', 'name', 'email', 'contact_type', 'subject',
                    'query', 'priority', 'subscribe', 'user_agent', 'ip_address'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

        return jsonify(
            {'success': True}
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

app.handler.csv_main.init_csv_files()
if __name__ == '__main__':
    init_csv_files()
    flask_app.run(host='0.0.0.0',debug = True)

