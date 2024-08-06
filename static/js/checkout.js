const inputElement = document.getElementById('my-address');
    const paymentForm = document.getElementById('make-payment');
    paymentForm.addEventListener("click", payWithPaystack, false);

    function payWithPaystack(e) {
      e.preventDefault();

      const form = document.getElementById('myFormAddress');

      // Check form validity before proceeding
      if (!form.checkValidity()) {
        const firstInvalid = form.querySelector(':required:invalid');
        if (firstInvalid) {
          firstInvalid.focus();
          return; // Prevent opening Paystack if form is invalid
        }
      }

      let handler = PaystackPop.setup({
        key: '{{paystack_public_key}}', // Replace with your public key
        email: '{{ request.user.email }}',
        currency: 'NGN',
        amount: '{{ get_cart_total }}' * 100,
        ref: '{{ payment.ref }}', // Replace with a unique reference if needed
        //onClose: function(){
        //  alert('There was an error with processing payment. Kindly refresh page and run again');
        //},
        callback: function(response){
          let message = 'Payment complete! Reference: ' + response.reference;

          var userData = {
                    'reference':response.reference
                }
            var url = '{% url 'process_order' %}'

            const enteredValue = inputElement.value; // Replace with logic to get address value

            fetch(url,
                {
                    method: 'POST',
                    headers: {'Content-Type': '/application/json', 'X-CSRFToken':csrftoken,},
                    body:JSON.stringify({'ref': userData, address: enteredValue})
                }
            )

            .then((response) =>{
                    return response.json()
                })

            .then((data) =>{
                    console.log('Success:', data);
                    //window.location.href = '/'
                    if (data.redirect) { // Check for 'redirect' key in response
                    window.location.href = data.redirect; // Redirect using client-side JavaScript
                  }

                })

          //console.log(message);
        }
      });

      handler.openIframe();
    }
