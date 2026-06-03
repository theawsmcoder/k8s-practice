1. use openssl to create a rsa key 
2. then create a cert signing request and sign it with that key.
    use CN (Common Name) for username and O (Organization) for group info in the subject of csr
3. sign this csr using ca.key. 
    it's better to create a CertificateSigningRequest for k8s admin to approve it
