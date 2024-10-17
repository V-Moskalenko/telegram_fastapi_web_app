import os
from datetime import datetime

from docxtpl import DocxTemplate


def fill_out_docx_template(application_data: dict):
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempate_docx.docx')
    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'temp', 'offer.docx')
    doc = DocxTemplate(template_path)
    all_total, num = 0, 1
    for serv in application_data['services']:
        serv['num'] = num
        serv[
            'name'] = f'{serv['training_program']}{(" " + serv['training_rank'] + " разряда") if serv['training_rank'] else ""}'
        serv['total'] = serv['people_count'] * serv['price']
        all_total += serv['total']
        num += 1
    application_data['all_total'] = all_total
    application_data['date_now'] = datetime.now().strftime('%d.%m.%Y')
    doc.render(application_data)
    doc.save(temp_file)
    return temp_file
