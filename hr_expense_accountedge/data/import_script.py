# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xmlrpclib
import base64
from datetime import datetime

username    = 'admin'   #the user
pwd         = 'admin'   #the password of the user
dbname      = 'testV10' #the database

# Get the uid
sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

# Search for exported expense notes
args = [('state', '=', 'exported')] #query clause
expense_ids = sock.execute(dbname, uid, pwd, 'hr.expense.expense', 'search', args)

# Outpout file for AccountEdge
final_csv = open('notes_de_frais_exportees.csv', 'w')

num_expense = 0

# For each exported expense note, search for he csv attachment
for expense_id in expense_ids:

    args    = [('res_model','=','hr.expense.expense'),('res_id', '=', expense_id)]
    csv_ids = sock.execute(dbname, uid, pwd, 'ir.attachment', 'search', args)

    fields  = ['name', 'datas'] #fields to read
    csv_obj = sock.execute(dbname, uid, pwd, 'ir.attachment', 'read', csv_ids, fields)

    latest_csv = None
    latest_date = datetime(2000, 1, 1, 0, 0, 0)

    # Find the latest csv
    for csv in csv_obj:
        format = 'rapport_%Y%m%d_%H%M%S'
        date_created = datetime.strptime(csv["name"], format)

        if date_created > latest_date:
            latest_date = date_created
            latest_csv = csv

    # Copy the lines to the new summary file
    if latest_csv:
        content     = base64.b64decode(csv['datas'])
        content     = content.split("\r\n")

        for num_line in range(len(content)):
            if (num_line == 1 and num_expense == 0) or num_line > 1:
                final_csv.write(content[num_line])
                final_csv.write("\r\n")


    num_expense = num_expense + 1


    # Mark the expenses as imported
    values = {'state': 'imported'}
    result = sock.execute(dbname, uid, pwd, 'hr.expense.expense', 'write', expense_ids, values)


final_csv.close()





