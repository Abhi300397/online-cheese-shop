$(function() {
      $('#btnSignUp').click(function() {
          var pat = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,12}$/
          var pwd = $('#inputPassword').val()
          if(pat.test(pwd)){

              $.ajax({
                  url: '/signUp',
                  data: $('form').serialize(),
                  type: 'POST',
                  success: function(response) {
                    if (response==="User registered successfully."){
                      alert(response)
                      $('#abtuser').html(response)
                    }
                    else if(response==='User already exists!! Try a different name or email id.')
                      $('#abtuser').html(response)
                  },
                  error: function(error) {
                      console.log(error);
                  }
              });
            }
          else{
              var txt = 'Password should be between 8 to 12 characters which contain at least one numeric digit, one uppercase and one lowercase letter'
              alert(txt)

            }



        });
    });