from flask import Flask, jsonify
import os
import datetime

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello from Jenkins Python Pipeline!',
        'version': '1.0.0',
        'build': os.environ.get('BUILD_NUMBER', 'dev'),
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

@app.route('/info')
def info():
    return jsonify({
        'app': 'Python Flask Demo',
        'jenkins_build': os.environ.get('BUILD_NUMBER', 'unknown'),
        'environment': 'jenkins-pipeline'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    """Entry point for console script"""
    import os
    port = int(os.environ.get('PORT', 5000))
                    print(f"🚀 Starting PEX Demo App on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
