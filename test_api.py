import requests

url = "http://127.0.0.1:5000/create_requests"

data = {
    "requestor_name": "John Doe",
    "title": "Adobe Creative Cloud Subscription",
    "vendor_name": "Adobe Systems",
    "vat_id": "DE123456789",
    "commodity_group": "Software Licenses",
    "total_cost": 3000,
    "department": "HR",
    "order_lines": [
        {
            "position_description": "Adobe Photoshop License",
            "unit_price": 200,
            "amount": 5,
            "unit": "licenses"
        },
        {
            "position_description": "Adobe Illustrator License",
            "unit_price": 250,
            "amount": 4,
            "unit": "licenses"
        }
    ]
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())