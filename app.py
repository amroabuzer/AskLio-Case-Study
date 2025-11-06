from flask import Flask, jsonify, request, render_template
from models import Request, OrderLine, db
from flask_cors import CORS

from extract_info import extract_info
import requests as reqs
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
db.init_app(app)

UPLOAD_FOLDER = 'uploads'
MAX_PDF_SIZE = 1
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with app.app_context():
    db.create_all()

@app.route('/create_requests', methods=['POST'])
def create_request():
    data = request.json
    
    new_request = Request(
        requester_name=data['requestor_name'],
        title=data['title'],
        vendor_name=data['vendor_name'],
        vat_id=data['vat_id'],
        commodity_group=data['commodity_group'],
        total_cost=data['total_cost'],
        department=data['department'],
        action=0,
    )
    
    for line in data.get('order_lines', []):
        order_line = OrderLine(
            position_description=line['Product'],
            unit_price=line['Unit Price'],
            amount=line['Quantity'],
            unit=line.get('unit'),
            total_price=line['Total']
        )
        new_request.order_lines.append(order_line)
        
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({'message': "Request created", "request_id": new_request.id}), 201

@app.route('/get_requests', methods=['GET'])
def get_request():
    requests = Request.query.all()
    
    result = []
    for req in requests:
        request_data = {
            'id': req.id,
            'requester_name': req.requester_name,
            'title': req.title,
            'vendor_name': req.vendor_name,
            'vat_id': req.vat_id,
            'commodity_group': req.commodity_group,
            'total_cost': req.total_cost,
            'department': req.department,
            'action': req.action,
            'order_lines': []
        }
        for line in req.order_lines:
            line_data = {
                'id': line.id,
                'Product': line.position_description,
                'Unit Price': line.unit_price,
                'Quantity': line.amount,
                'unit': line.unit,
                'Total': line.total_price
            }
            request_data['order_lines'].append(line_data)
        
        result.append(request_data)
    
    return jsonify(result), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    _, file_ext = os.path.splitext(file_path)
    if file_ext.lower() != '.pdf':
        print(os.path.splitext(file_path)[1])
        return jsonify({"message": f"Only PDF files are allowed, you submitted a {file_ext.lower()}"}), 400
    file_size = file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    file_size /= (1024 * 1024)
    if file_size > MAX_PDF_SIZE:
        return jsonify({"message": f"PDF cannot exceed {MAX_PDF_SIZE} MB"}), 400

    file.save(file_path)

    extracted_dictionary = extract_info(file_path)
    data = {
        "requestor_name": "-",
        "title": "-",
        "vendor_name": extracted_dictionary["Vendor Name"],
        "vat_id": extracted_dictionary["USt-IdNr"],
        "commodity_group": extracted_dictionary["Commodity Group"],
        "total_cost": extracted_dictionary["Total Cost"],
        "department": extracted_dictionary["Requestor Department"],
        "order_lines": extracted_dictionary["Order Lines"]
    }
    print(extracted_dictionary["Order Lines"])
    response = reqs.post("http://127.0.0.1:5000/create_requests", json=data)
    print(response.status_code)
    print(response.json())
    return jsonify({"message": f"File '{file.filename}' uploaded successfully!"})

@app.route("/update_action/<int:request_id>", methods=["POST"])
def update_status(request_id):
    data = request.get_json()  # get JSON body
    if not data or "action" not in data:
        return jsonify({"error": "Missing 'action' in request"}), 400

    requests = Request.query.all()
    req = next((r for r in requests if r.id == request_id), None)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.action = data['action']
    db.session.commit()

    return jsonify({"message": f"Status updated to {data['action']}"})

@app.route('/update_request/<int:request_id>', methods=['POST'])
def update_request(request_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    for field, value in data.items():
        print(req.requester_name)
        print(value)
        print(getattr(req, field))
        if hasattr(req, field):
            setattr(req, field, value)
    
    db.session.commit()
    return jsonify({"message": f"Request {request_id} updated successfully"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)