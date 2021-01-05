# Export Contacts

First connect to your PostgreSQL database with psql.
If you're using Heroku, this is as simple as installing psql and the heroku cli
then running:
```bash
heroku pg:psql -a myhackerforce
```

Once you have psql running, use the following to export contacts to
`contacts.csv` on your local machine:
```sql
\copy (SELECT name,first_name,last_name,position,email,contacts_contact.notes FROM contacts_contact INNER JOIN companies_company ON company_id = companies_company.id ORDER BY name) to 'contacts.csv' with csv
```
