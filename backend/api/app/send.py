import boto3
from botocore.exceptions import ClientError
from reportlab.pdfgen import canvas

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import navy, black
from reportlab.pdfbase.pdfmetrics import stringWidth

client = boto3.client('ses',region_name="us-east-2")


def format_plaid_income(pdf, width, height, employerName, employerStreet, employerTownAndZip, employerPhone,
                        employeeName, employeeStreet, employeeTownAndZip,
                        payPeriodStart, payPeriodEnd, payDate,
                        grossEarnings, totalTaxesAndDeductions, netPay, bankName, bankMask,
                        currentSalary, ytdSalary, currentSupplementalBonus, ytdSupplementalBonus, currentTotalEarnings, ytdTotalEarnings,
                        currentFederalIncomeTax, currentSocialSecurity, currentMedicare, currentStateTax, currentTotalTaxWithheld, ytdTotalTaxWithheld):
    # Add CaseSwift Header
    headerString = "CaseSwift Income Verification Statement"
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(navy)
    headerStringWidth = stringWidth(headerString, "Helvetica-Bold", 10)
    pdf.drawString((width - headerStringWidth)/2, height-(0.75*inch), headerString)
    pdf.line((width/2)-(headerStringWidth/2), height-(inch*0.85), (width/2)+(headerStringWidth/2), height-(inch*0.85))

    # Draw Employer Information
    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(1.2*inch), "Employer:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString((inch*1.1), height-(1.4*inch), employerName)
    pdf.drawString((inch*1.1), height-(1.6*inch), employerStreet)
    pdf.drawString((inch*1.1), height-(1.8*inch), employerTownAndZip)
    pdf.drawString((inch*1.1), height-(2*inch), employerPhone)

    # Draw Employee Information
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawRightString(width-(inch*1.1), height-(1.2*inch), "Employee:")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(1.4*inch), employeeName)
    pdf.drawRightString(width-(inch*1.1), height-(1.6*inch), employeeStreet)
    pdf.drawRightString(width-(inch*1.1), height-(1.8*inch), employeeTownAndZip)

    # Box Employer/Employee
    pdf.setFont("Helvetica-Bold", 10)
    pdf.rect(0.9*inch, height-(2.1*inch), width-(1.8*inch), inch*1.1)

    # Draw Pay Period Information
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(2.5*inch), "Pay Period Start: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(2.5*inch), payPeriodStart)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(2.7*inch), "Pay Period End: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(2.7*inch), payPeriodEnd)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(2.9*inch), "Pay Date: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(2.9*inch), payDate)

    #Box Pay Period Information
    pdf.setFont("Helvetica-Bold", 10)
    pdf.rect(0.9*inch, height-(3*inch), (width-(1.8*inch)), inch*0.7)

    # Draw Payment Summary Information
    pdf.setFont("Helvetica-Bold", 10)
    paymentSummaryStringWidth = stringWidth("Payment Summary", "Helvetica-Bold", 10)
    pdf.drawString((width - paymentSummaryStringWidth)/2, height-(3.2*inch), "Payment Summary")

    pdf.drawString((inch*1.1), height-(3.4*inch), "Gross Earnings: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(3.4*inch), grossEarnings)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(3.6*inch), "Total Taxes and Deductions: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(3.6*inch), totalTaxesAndDeductions)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(3.8*inch), "Net Pay: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(3.8*inch), netPay)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(4*inch), "Direct Deposit To: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(4*inch), bankName + "-" + bankMask)

    # Box Payment Summary Information
    pdf.setFont("Helvetica-Bold", 10)
    pdf.rect(0.9*inch, height-(4.1*inch), width-(1.8*inch), inch*1.1)

    # Draw Gross Earnings Section
    pdf.setFont("Helvetica-Bold", 10)
    grossEarningsSummaryWidth = stringWidth("Gross Earnings", "Helvetica-Bold", 10)
    pdf.drawString((width - grossEarningsSummaryWidth)/2, height-(4.3*inch), "Gross Earnings")
    
    pdf.drawString((inch*1.1), height-(4.5*inch), "Description")
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-currentStringWidth)/2, height-(4.5*inch), "Current")
    pdf.drawRightString((width-(inch*1.1)), height-(4.5*inch), "YTD")

    pdf.setFont("Helvetica", 10)
    pdf.drawString((inch*1.1), height-(4.7*inch), "Salary")
    currentSalaryWidth = stringWidth(currentSalary, "Helvetica", 10)
    pdf.drawString((width-currentSalaryWidth)/2, height-(4.7*inch), currentSalary)
    pdf.drawRightString((width-(inch*1.1)), height-(4.7*inch), ytdSalary)

    pdf.drawString((inch*1.1), height-(4.9*inch), "Supplemental pay: Bonus")
    currentSupplementalBonusWidth = stringWidth(currentSupplementalBonus, "Helvetica", 10)
    pdf.drawString((width-currentSupplementalBonusWidth)/2, height-(4.9*inch), currentSupplementalBonus)
    pdf.drawRightString((width-(inch*1.1)), height-(4.9*inch), ytdSupplementalBonus)

    pdf.line((inch*1.1), height-(5.0*inch), width-(inch*1.1), height-(5.0*inch))

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(5.2*inch), "Gross Earnings Totals")
    currentTotalWidth = stringWidth(currentTotalEarnings, "Helvetica-Bold", 10)
    pdf.drawString((width-currentTotalWidth)/2, height-(5.2*inch), currentTotalEarnings)
    pdf.drawRightString((width-(inch*1.1)), height-(5.2*inch), ytdTotalEarnings)

    # Box Gross Earnings Section
    pdf.setFont("Helvetica-Bold", 10)
    pdf.rect(0.9*inch, height-(5.3*inch), width-(1.8*inch), inch*1.2)

    # Draw Taxes Withheld Section
    pdf.setFont("Helvetica-Bold", 10)
    taxesWithheldWidth = stringWidth("Taxes Withheld", "Helvetica-Bold", 10)
    pdf.drawString((width - taxesWithheldWidth)/2, height-(5.5*inch), "Taxes Withheld")

    pdf.drawString((inch*1.1), height-(5.7*inch), "Description")
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-currentStringWidth)/2, height-(5.7*inch), "Current")
    pdf.drawRightString((width-(inch*1.1)), height-(5.7*inch), "YTD")

    pdf.setFont("Helvetica", 10)
    pdf.drawString((inch*1.1), height-(5.9*inch), "Federal Income Tax")
    currentFederalIncomeTaxWidth = stringWidth(currentFederalIncomeTax, "Helvetica", 10)
    pdf.drawString((width-currentFederalIncomeTaxWidth)/2, height-(5.9*inch), currentFederalIncomeTax)

    pdf.drawString((inch*1.1), height-(6.1*inch), "Social Security")
    currentSocialSecurityWidth = stringWidth(currentSocialSecurity, "Helvetica", 10)
    pdf.drawString((width-currentSocialSecurityWidth)/2, height-(6.1*inch), currentSocialSecurity)

    pdf.drawString((inch*1.1), height-(6.3*inch), "Medicare")
    currentMedicareWidth = stringWidth(currentMedicare, "Helvetica", 10)
    pdf.drawString((width-currentMedicareWidth)/2, height-(6.3*inch), currentMedicare)

    pdf.drawString((inch*1.1), height-(6.5*inch), "State Income Tax")
    currentStateTaxWidth = stringWidth(currentStateTax, "Helvetica", 10)
    pdf.drawString((width-currentStateTaxWidth)/2, height-(6.5*inch), currentStateTax)

    pdf.line((inch*1.1), height-(6.6*inch), width-(inch*1.1), height-(6.6*inch))

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString((inch*1.1), height-(6.8*inch), "Taxes Withheld Totals")
    currentTotalTaxesWidth = stringWidth(currentTotalTaxWithheld, "Helvetica-Bold", 10)
    pdf.drawString((width-currentTotalTaxesWidth)/2, height-(6.8*inch), currentTotalTaxWithheld)
    pdf.drawRightString((width-(inch*1.1)), height-(6.8*inch), ytdTotalTaxWithheld)

    # Box Taxes Withheld Section
    pdf.setFont("Helvetica-Bold", 6)
    pdf.rect(0.9*inch, height-(6.9*inch), width-(1.8*inch), inch*1.6)

    pdf.setFillColor(navy)
    footerMessage = "Information Provided by CaseSwift: The GOAT PI SAAS Platform"
    footerLength = stringWidth(footerMessage, "Helvetica-Bold", 6)
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-footerLength)/2, height-(10.5*inch), footerMessage)

    return pdf   
    
msg = MIMEMultipart()
msg['Subject'] = 'Your Requested Documents from CaseSwift'
msg['From'] = 'jordan@caseswift.io'
msg['To'] = 'jordan@caseswift.io'

# what a recipient sees if they don't use an email reader
msg.preamble = 'CaseSwift Documents.\n'

# the message body
part = MIMEText('Howdy -- here are your requested Documents')
msg.attach(part)

plaidFinancialInformationPdf = canvas.Canvas("plaid_income_verification.pdf", pagesize=letter)
width, height = letter
format_plaid_income(plaidFinancialInformationPdf, width, height, "CaseSwift LLC", "1309 Hill Street", "Durham, NC 27707", "(123) 456-7890",
                    "Jordan Castleman", "445 W 35th Street", "New York, New York 10001",
                    "2020-12-15", "2021-12-15", "2021-6-15",
                    "$123,456", "$123,456", "$123,456", "Bank of America", "1234",
                    "123,456", "$123,456", "123", "$0", "$123,456", "$123,456",
                    "$123,456", "$123,456", "$123,456", "$123,456", "$123,456", "$123,456")
plaidFinancialInformationPdf.showPage()
plaidFinancialInformationPdf.save()

# the attachment
part = MIMEApplication(open('plaid_income_verification.pdf', 'rb').read())
part.add_header('Content-Disposition', 'attachment', filename='plaid_income_verification.pdf')
msg.attach(part)


# and send the message
try: 

    response = client.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={
        'Data': msg.as_string()
    },)

except ClientError as e:
    print(e.response['Error']['Message'])
else:
    print("Email sent! Message ID:"),
    print(response['MessageId'])


