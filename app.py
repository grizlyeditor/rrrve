from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import random
import time
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = 'zatrdev_secret_key_2024'

# XP Requirements for levels 1 to 100
XP_REQUIREMENTS = {
    1: 400, 2: 800, 3: 1200, 4: 1600, 5: 2000, 6: 2400, 7: 2800, 8: 3200, 9: 3600, 10: 4000,
    11: 4400, 12: 4800, 13: 5200, 14: 5600, 15: 6000, 16: 6400, 17: 6800, 18: 7200, 19: 7600, 20: 8000,
    21: 8400, 22: 8800, 23: 9200, 24: 9600, 25: 10000, 26: 10400, 27: 10800, 28: 11200, 29: 11600, 30: 12000,
    31: 12400, 32: 12800, 33: 13200, 34: 13600, 35: 14000, 36: 14400, 37: 14800, 38: 15200, 39: 15600, 40: 16000,
    41: 16400, 42: 16800, 43: 17200, 44: 17600, 45: 18000, 46: 18400, 47: 18800, 48: 19200, 49: 19600, 50: 20000,
    51: 20400, 52: 20800, 53: 21200, 54: 21600, 55: 22000, 56: 22400, 57: 22800, 58: 23200, 59: 23600, 60: 24000,
    61: 24400, 62: 24800, 63: 25200, 64: 25600, 65: 26000, 66: 26400, 67: 26800, 68: 27200, 69: 27600, 70: 28000,
    71: 28400, 72: 28800, 73: 29200, 74: 29600, 75: 30000, 76: 30400, 77: 30800, 78: 31200, 79: 31600, 80: 32000,
    81: 32400, 82: 32800, 83: 33200, 84: 33600, 85: 34000, 86: 34400, 87: 34800, 88: 35200, 89: 35600, 90: 36000,
    91: 36400, 92: 36800, 93: 37200, 94: 37600, 95: 38000, 96: 38400, 97: 38800, 98: 39200, 99: 39600, 100: 40000
}

# Store active bots
active_bots = {}

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def calculate_xp_progress(current_level, current_xp):
    xp_required = XP_REQUIREMENTS.get(current_level, 40000)
    xp_for_current_level = XP_REQUIREMENTS.get(current_level - 1, 0)
    current_level_xp = current_xp - xp_for_current_level
    progress_percentage = (current_level_xp / xp_required) * 100
    return min(progress_percentage, 100), xp_required

def bot_simulation(job_id, job_data):
    while job_id in active_bots:
        try:
            # Simulate XP gain every 4 seconds
            time.sleep(4)
            
            if job_id not in active_bots:
                break
                
            # Add random XP (44 as mentioned)
            xp_gain = 44
            job_data['current_xp'] += xp_gain
            job_data['bot_matches'] += 1
            job_data['recent_xp'] = xp_gain
            
            # Check if level up
            current_level = job_data['current_level']
            xp_required = XP_REQUIREMENTS.get(current_level, 40000)
            
            if job_data['current_xp'] >= xp_required and current_level < 100:
                job_data['current_level'] += 1
                job_data['level_up'] = True
            
            # Update job data
            active_bots[job_id] = job_data
            
        except Exception as e:
            print(f"Bot error: {e}")
            break

@app.route('/')
def index():
    jobs = session.get('jobs', [])
    return render_template('index.html', jobs=jobs)

@app.route('/create_job', methods=['POST'])
def create_job():
    try:
        job_name = request.form.get('job_name')
        uid = request.form.get('uid')
        password = request.form.get('password')
        
        # Simulate API call to get account info
        # In real implementation, you would call: https://info-api-dev.vercel.app/get?uid=5780114069&server_name={region}
        account_info = {
            'AccountInfo': {
                'AccountLevel': 53,
                'AccountEXP': 436559,
                'AccountName': 'TestPlayer',
                'AccountRegion': 'ID'
            }
        }
        
        new_job = {
            'id': str(int(time.time())),
            'name': job_name,
            'uid': uid,
            'password': password,
            'account_info': account_info,
            'status': 'Offline',
            'current_level': account_info['AccountInfo']['AccountLevel'],
            'current_xp': account_info['AccountInfo']['AccountEXP'],
            'random_ip': generate_random_ip(),
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'bot_matches': 0,
            'recent_xp': 0,
            'level_up': False
        }
        
        # Save to session
        jobs = session.get('jobs', [])
        jobs.append(new_job)
        session['jobs'] = jobs
        
        return jsonify({'success': True, 'message': 'Job created successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/job/<job_id>')
def job_details(job_id):
    jobs = session.get('jobs', [])
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if not job:
        return redirect(url_for('index'))
    
    progress_percentage, xp_required = calculate_xp_progress(job['current_level'], job['current_xp'])
    
    return render_template('job_details.html', 
                         job=job, 
                         progress_percentage=progress_percentage,
                         xp_required=xp_required,
                         xp_requirements=XP_REQUIREMENTS)

@app.route('/start_bot/<job_id>')
def start_bot(job_id):
    jobs = session.get('jobs', [])
    job_index = next((i for i, j in enumerate(jobs) if j['id'] == job_id), None)
    
    if job_index is not None:
        jobs[job_index]['status'] = 'Online'
        session['jobs'] = jobs
        
        # Start bot simulation
        if job_id not in active_bots:
            active_bots[job_id] = jobs[job_index].copy()
            bot_thread = threading.Thread(target=bot_simulation, args=(job_id, active_bots[job_id]))
            bot_thread.daemon = True
            bot_thread.start()
        
        return jsonify({'success': True, 'message': 'Bot started'})
    
    return jsonify({'success': False, 'message': 'Job not found'})

@app.route('/stop_bot/<job_id>')
def stop_bot(job_id):
    if job_id in active_bots:
        del active_bots[job_id]
    
    jobs = session.get('jobs', [])
    job_index = next((i for i, j in enumerate(jobs) if j['id'] == job_id), None)
    
    if job_index is not None:
        jobs[job_index]['status'] = 'Offline'
        session['jobs'] = jobs
    
    return jsonify({'success': True, 'message': 'Bot stopped'})

@app.route('/refresh_job/<job_id>')
def refresh_job(job_id):
    jobs = session.get('jobs', [])
    job_index = next((i for i, j in enumerate(jobs) if j['id'] == job_id), None)
    
    if job_index is not None and job_id in active_bots:
        # Update from active bot data
        bot_data = active_bots[job_id]
        jobs[job_index].update({
            'current_level': bot_data['current_level'],
            'current_xp': bot_data['current_xp'],
            'bot_matches': bot_data['bot_matches'],
            'recent_xp': bot_data['recent_xp'],
            'level_up': bot_data.get('level_up', False)
        })
        
        if jobs[job_index]['level_up']:
            jobs[job_index]['level_up'] = False
            active_bots[job_id]['level_up'] = False
        
        session['jobs'] = jobs
    
    return jsonify({'success': True})

@app.route('/get_job_data/<job_id>')
def get_job_data(job_id):
    jobs = session.get('jobs', [])
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if job:
        progress_percentage, xp_required = calculate_xp_progress(job['current_level'], job['current_xp'])
        
        return jsonify({
            'success': True,
            'job': job,
            'progress_percentage': progress_percentage,
            'xp_required': xp_required
        })
    
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
