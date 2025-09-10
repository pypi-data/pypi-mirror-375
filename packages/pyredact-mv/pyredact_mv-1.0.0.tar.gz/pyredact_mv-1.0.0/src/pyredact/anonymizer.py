pseudo_user_id_counter = 1

def anonymize_email(email: str) -> str:
    global pseudo_user_id_counter
    _user, domain = email.split('@')
    anonymized_user = f"user_{pseudo_user_id_counter}"
    pseudo_user_id_counter += 1
    return f"{anonymized_user}@{domain}"

def anonymize_phone_number(phone: str) -> str:
    clean_phone = ''.join(filter(str.isdigit, phone))
    if len(clean_phone) > 4:
        return f"{'*' * (len(clean_phone) - 4)}{clean_phone[-4:]}"
    return 'X' * len(phone)

def anonymize_payment_card(card: str) -> str:
    clean_card = card.replace(' ', '').replace('-', '')
    return f"{'*' * (len(clean_card) - 4)}{clean_card[-4:]}"

def anonymize_cvv(cvv: str) -> str:
    return '*' * len(cvv)

def anonymize_dob(dob: str) -> str:
    parts = dob.replace('/', '-').split('-')
    return f"XX-XX-{parts[-1]}"

def anonymize_ip_address(ip: str) -> str:
    parts = ip.split('.')
    return f"***.***.***.{parts[-1]}"
    
def anonymize_full_redaction(value: str) -> str:
    return 'X' * len(value)

def anonymize_indian_mobile(mobile: str) -> str:
    clean_mobile = mobile.replace(' ', '').replace('-', '').replace('+91', '')
    if len(clean_mobile) > 4:
        return f"{clean_mobile[:2]}******{clean_mobile[-2:]}"
    return 'X' * len(mobile)

def anonymize_aadhaar(aadhaar: str) -> str:
    clean_aadhaar = aadhaar.replace(' ', '').replace('-', '')
    return f"{clean_aadhaar[:4]}-XXXX-{clean_aadhaar[-4:]}"

def anonymize_ifsc_code(ifsc: str) -> str:
    return f"{ifsc[:4]}XXXXXXX"

def anonymize_indian_bank_account(account_num: str) -> str:
    return f"{'*' * (len(account_num) - 4)}{account_num[-4:]}"

ANONYMIZATION_RULES = {
    'EMAIL': anonymize_email,
    'PHONE_NUMBER': anonymize_phone_number,
    'PAYMENT_CARD_NUMBER': anonymize_payment_card,
    'CVV': anonymize_cvv,
    'DOB': anonymize_dob,
    'IP_ADDRESS': anonymize_ip_address,
    'INDIAN_MOBILE': anonymize_indian_mobile,
    'AADHAAR': anonymize_aadhaar,
    'PAN_CARD': anonymize_full_redaction,
    'VOTER_ID': anonymize_full_redaction,
    'IFSC_CODE': anonymize_ifsc_code,
    'INDIAN_BANK_ACCOUNT': anonymize_indian_bank_account,
    'INDIAN_PASSPORT': anonymize_full_redaction,
}

def anonymize_pii(pii_type: str, pii_value: str) -> str:
    anonymizer_func = ANONYMIZATION_RULES.get(pii_type)
    if anonymizer_func:
        return anonymizer_func(pii_value)
    return pii_value