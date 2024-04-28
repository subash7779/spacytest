from django.shortcuts import render, redirect
from myapp.utils import extract_text_from_pdf, get_entities, OriginalData, MaskedData
from django.template.defaultfilters import linebreaks

def dashboard(request):
    username = request.session.get('username')
    usertype = request.session.get('usertype')

    if 'username' not in request.session:
        return redirect('user_login')
    if 'usertype' not in request.session:
        return redirect('user_login')
    doc_type = request.GET.get('doc')

    if username:
        process_data = ''
        if doc_type:
            page_text = extract_text_from_pdf(doc_type)
            entities = get_entities(page_text)
            
            if page_text and entities:
                access_levels = {
                    "ADMIN": {"PAYSLIP": "unmasked", "TAX_INVOICE": "unmasked"},
                    "MANAGER": {"PAYSLIP": "masked", "TAX_INVOICE": "unmasked"},
                    "EMPLOYEE": {"PAYSLIP": "unmasked", "TAX_INVOICE": "masked"}
                }
                access_level = access_levels.get(usertype, {}).get(doc_type.upper(), "masked")
                if usertype=="EMPLOYEE" and doc_type=="TAX_INVOICE":
                    process_data = "<h5 class='text-danger text-center'>You do not have access to view this document.</h5>"
                elif access_level == "unmasked":
                    process_data = OriginalData(page_text)
                elif access_level == "masked":
                    process_data = MaskedData(entities, page_text)
            
        return render(request, 'dashboard.html', {'username': username, 'usertype': usertype, 'process_data': linebreaks(process_data)})
    else:
        return redirect('user_login')
    
def demo(request):
    username = request.session.get('username')
    usertype = request.session.get('usertype')
    input_text = ''
    masked_text = ''
    if request.method == "POST":
        input_text = request.POST.get('input_text').strip()
        entities = get_entities(input_text)
        masked_text = MaskedData(entities, input_text)

        print("masked_text", masked_text)
    return render(request, 'demo.html', {'username': username, 'usertype': usertype, 'input_text' : input_text, 'masked_text': masked_text.replace('\n', '<br />')})