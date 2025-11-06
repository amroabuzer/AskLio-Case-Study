model_name = "gpt-4-turbo"

template_procurement_dictionary = {
    "Vendor Name": str,
    "USt-IdNr": str,
    "Total Cost": str,
    "Requestor Department": str,
    "Order Lines": list,
}
template_order_list = {
"Product": str,
"Unit Price": str,
"Quantity": str,
"Total": str
}

commodity_group_categories = [
    "Accommodation Rentals",
    "Membership Fees",
    "Workplace Safety",
    "Consulting",
    "Financial Services",
    "Fleet Management",
    "Recruitment Services",
    "Professional Development",
    "Miscellaneous Services",
    "Insurance",
    "Electrical Engineering",
    "Facility Management Services",
    "Security",
    "Renovations",
    "Office Equipment",
    "Energy Management",
    "Maintenance",
    "Cafeteria and Kitchenettes",
    "Cleaning",
    "Audio and Visual Production",
    "Books/Videos/CDs",
    "Printing Costs",
    "Software Development for Publishing",
    "Material Costs",
    "Shipping for Production",
    "Digital Product Development",
    "Post-production Costs",
    "Hardware",
    "IT Services",
    "Software",
    "Courier, Express, and Postal Services",
    "Warehousing and Material Handling",
    "Transportation Logistics",
    "Delivery Services",
    "Advertising",
    "Outdoor Advertising",
    "Marketing Agencies",
    "Direct Mail",
    "Customer Communication",
    "Online Marketing",
    "Events",
    "Promotional Materials",
    "Warehouse and Operational Equipment",
    "Production Machinery",
    "Spare Parts",
    "Internal Transportation",
    "Production Materials",
    "Consumables",
    "Maintenance and Repairs"
]

pdf_extractor_prompt_template = """
Prompt for Procurement Information Extraction
Role:
You are a highly accurate information extraction AI specialized in procurement document analysis.
You are working under Lio Technologies GmbH.
You will be given a PDF document (e.g., invoice, purchase order, or quotation). 
Your task is to carefully read and extract only the information that is explicitly present in the document.

Instructions:
1- Extract the procurement details following exactly the template below.
2- If any information is missing, unclear, or not explicitly stated, write a single hyphen - instead of making assumptions.
3- Maintain the format, order, and structure precisely as given.
4- Preserve the currency symbol and formatting exactly as it appears in the document (e.g., €, $, £).
5- Ensure all numerical values are captured accurately as well as Integer or Float castable.
6- Do not include any commentary, reasoning, or explanations — only provide the structured output.

Output Template
{
    "Vendor Name": [Extracted or -],
    "USt-IdNr": [Extracted or -],
    "Requestor Department": [Extracted or -],
    "Order Lines": [
        {
            "Product": [Extracted or -],
            "Unit Price": [Extracted or -], 
            "Quantity": [Extracted or -],
            "Total": [Extracted or -]
        },
        (Add more items if present in document.)
    ]
    "Total Cost": [Extracted or -]
}

Example Output:
{
    "Vendor Name": "Global Tech Solutions",
    "USt-IdNr": "DE987654321",
    "Requestor Department": "Creative Marketing Department",
    "Order Lines": [
        {
            "Product": "Adobe Photoshop License",
            "Unit Price": "€150", 
            "Quantity": "10",
            "Total": "€1500"
        },
        {
            "Product": "Adobe Illustrator License",
            "Unit Price": "€120"
            "Quantity": "5"
            "Total": "€600"
        }
    ]
    "Total Cost": "€2100"
}

"""

categorize_prompt = f"""
You are an expert classifier. 
You will be given the text content extracted from a PDF document. 
Your task is to categorize the document into exactly one of the following categories:

{commodity_group_categories}

Instructions:
- Read the document carefully.
- Choose the single category that best fits the entire document.
- Output ONLY the name of the chosen category. Do NOT include explanations, punctuation, or any additional text.
"""