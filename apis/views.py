from django.shortcuts import render

# Create your views here.

#========================================
# This api is to check whether email exists
# on system or not while sign up.
#========================================
@csrf_exempt
@api_view(['POST'])
def check_email(request):
    try:
        with transaction.atomic():
            lock = Lock()
            lock.acquire()  # will block if another thread has lock
            try:
                received_json_data = json.loads(request.body, strict=False)
                try:
                    
                    authy_api = AuthyApiClient('#your_api_key')
                    
                    user = User.objects.get(email = received_json_data['email'])
                    return Response({"message" : errorEmailExist, "status" : "0"}, status=status.HTTP_409_CONFLICT)
                except:
                    try:
                        
                        tempuser = TempUserEmail.objects.get(email = received_json_data['email'])
                        return Response({"message" : errorEmailExist, "status" : "0"}, status=status.HTTP_409_CONFLICT)
                    except:
                        TempUserEmail.objects.create(id = None, email = received_json_data['email'])
                        return Response({"message" : emailAvailableMessage, "status" : "1"}, status=status.HTTP_200_OK)
            finally:
                lock.release()
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# This api is for Sign Up a new user.
#========================================
@csrf_exempt
@api_view(['POST'])
def sign_up(request):
    try:
        with transaction.atomic():
            lock = Lock()
            lock.acquire()  # will block if another thread has lock
            try:
                received_json_data = json.loads(request.body, strict=False)
                try:
                    user = User.objects.get(email = received_json_data['email'])
                    return Response({"message" : errorEmailExist, "status" : "0"}, status=status.HTTP_409_CONFLICT)
                except:
                    user = User.objects.create(email = received_json_data['email'],
                                        first_name = received_json_data['first_name'],
                                        last_name = received_json_data['last_name'],
                                        username = received_json_data['email'],
                                        password = received_json_data['password'],
                                        sign_up_status = SIGN_UP_STATUS_EMAIL)
                    authUser = authenticate(username=received_json_data['email'], password=received_json_data['password'])
                    token = ''
                    try:
                        user_with_token = Token.objects.get(user=user)
                    except:
                        user_with_token = None
                    
                    if user_with_token is None:
                        token1 = Token.objects.create(user=user)
                        token = token1.key
                    else:
                        Token.objects.get(user=user).delete()
                        token1 = Token.objects.create(user=user)
                        token = token1.key
                    return Response({"message" : addSuccessMessage, "token" : token, "status" : "1"}, status=status.HTTP_201_CREATED)
                    
            finally:
                lock.release()
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# To send OTP to verify mobile number of
# user while doing sign up process
#========================================
@csrf_exempt
@api_view(['POST'])
def send_otp(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            authy_api = AuthyApiClient(authy_auth_token)
            phone = authy_api.phones.verification_start(
                received_json_data['phone'],
                received_json_data['phone_country_code'],
                via='sms'
            )
            
            if phone.ok():
                return Response({"message" : otpSuccessMessage, "status" : "1"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : phone.errors(), "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#========================================
# To check OTP to verify a user's phone numberemail = received_json_data['email']
#========================================
@csrf_exempt
@api_view(['POST'])
def check_otp(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            authy_api = AuthyApiClient(authy_auth_token)
            
            verification = authy_api.phones.verification_check(
                received_json_data['phone'],
                received_json_data['phone_country_code'],
                received_json_data['otp']
            )
            
            if verification.ok():
                User.objects.filter(id = user.id).update(phone = received_json_data['phone_country_code'] + received_json_data['phone'])
                return Response({"message" : otpMatchSuccessMessage, "status" : "1"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : verification.errors(), "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# Email Login Api
#========================================
@csrf_exempt
@api_view(['POST'])
def login(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
            user = authenticate(username=received_json_data['email'], password=received_json_data['password'])
            if user is not None:
                if user.is_active:
                    if user.phone is None or user.phone == "":
                        return Response({"message" : errorIncompleteProfile, "status" : "-1"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing phone number
                    else:
                        if user.want_to_invite_friends == -1:
                            return Response({"message" : errorIncompleteProfile, "status" : "0"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing invite friends
                        else:
                            if user.role == -1:
                                return Response({"message" : errorIncompleteProfile, "status" : "0"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing role
                            else:
                                token = ''
                                try:
                                    user_with_token = Token.objects.get(user=user)
                                except:
                                    user_with_token = None
                                
                                if user_with_token is None:
                                    token1 = Token.objects.create(user=user)
                                    token = token1.key
                                else:
                                    Token.objects.get(user=user).delete()
                                    token1 = Token.objects.create(user=user)
                                    token = token1.key
                                return Response({"message" : loginSuccessMessage, "token" : token, "status" : "1"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorBlockedAcount, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message" : errorEmailPasswordIncorrect, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# Social Login Api
#========================================
@csrf_exempt
@api_view(['POST'])
def social_login(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
            user = authenticate(username=received_json_data['social_id'], password=received_json_data['social_id'])
            if user is not None:
                if user.is_active:
                    if user.phone is None or user.phone == "":
                        return Response({"message" : errorIncompleteProfile, "status" : "-1"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing phone number
                    else:
                        if user.want_to_invite_friends == -1:
                            return Response({"message" : errorIncompleteProfile, "status" : "0"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing invite friends
                        else:
                            if user.role == -1:
                                return Response({"message" : errorIncompleteProfile, "status" : "0"}, status=status.HTTP_406_NOT_ACCEPTABLE) #This will represent missing role
                            else:
                                token = ''
                                try:
                                    user_with_token = Token.objects.get(user=user)
                                except:
                                    user_with_token = None
                                
                                if user_with_token is None:
                                    token1 = Token.objects.create(user=user)
                                    token = token1.key
                                else:
                                    Token.objects.get(user=user).delete()
                                    token1 = Token.objects.create(user=user)
                                    token = token1.key
                                return Response({"message" : loginSuccessMessage, "token" : token, "status" : "1"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorBlockedAcount, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                email = received_json_data['email']
                try:
                    user = User.objects.get(email = email)
                    return Response({"message" : errorEmailExist, "status" : "0"}, status=status.HTTP_409_CONFLICT)
                except:
                    user = User.objects.create(email = received_json_data['email'],
                                        first_name = received_json_data['first_name'],
                                        last_name = received_json_data['last_name'],
                                        username = received_json_data['social_id'],
                                        password = received_json_data['social_id'])
                    if user is not None:
                        if received_json_data['phone'] is not None and received_json_data['phone'] != "":
                            User.objects.filter(id = user.id).update(phone = received_json_data['phone'])
                        if received_json_data['login_type'] == "facebook":
                            User.objects.filter(id = user.id).update(sign_up_status = SIGN_UP_STATUS_FACEBOOK)
                        if received_json_data['login_type'] == "google":
                            User.objects.filter(id = user.id).update(sign_up_status = SIGN_UP_STATUS_GOOGLE)
                        if received_json_data['image'] is not None and received_json_data['image'] != "":
                            profilePicName = received_json_data['first_name']+'.jpg'
                            try:
                                format, tempString = request.data['image'].split(';base64,')
                            except:
                                tempString = ""
                            
                            if tempString == "":
                                tempString = request.data['profile_pic']
                            
                            image_64_decode = base64.decodestring(tempString) 
                            fh = default_storage.open("profilepic/" + user.id + "/" + profilePicName, 'w')  # create a writable image and write the decoding result
                            fh.write(image_64_decode)
                            fh.close()
                            profile_pic_url = settings.MEDIA_URL + "profilepic/" + user.id + "/" + profilePicName
                            User.objects.filter(id = user.id).update(image = profile_pic_url)
                        token = ''
                        try:
                            user_with_token = Token.objects.get(user=user)
                        except:
                            user_with_token = None
                        
                        if user_with_token is None:
                            token1 = Token.objects.create(user=user)
                            token = token1.key
                        else:
                            Token.objects.get(user=user).delete()
                            token1 = Token.objects.create(user=user)
                            token = token1.key
                        return Response({"message" : addSuccessMessage, "token" : token, "status" : "1"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# API to get user details
#========================================
@csrf_exempt
@api_view(['GET'])
def get_profile_info(request):
    try:
        with transaction.atomic():
            
            received_json_data = json.loads(request.body, strict=False)
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            
            user_detail = {"last_login" : user.last_login,
                           "username" : user.username,
                            "first_name" : user.first_name,
                            "last_name" : user.last_name,
                            "email" : user.email,
                            "date_joined" : user.date_joined,
                            "phone" : user.phone,
                            "country" : user.country,
                            "city" : user.city,
                            "address" : user.address,
                            "zip" : user.zip,
                            "image" : user.image,
                            "sign_up_status" : user.sign_up_status,
                            "social_id" : user.social_id}

            return Response({"message" : loginSuccessMessage, "data" : user_detail, "status" : "1"}, status=status.HTTP_200_OK)
            
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================
# Update User Profile API
#========================================
@csrf_exempt
@api_view(['PUT'])
def update_profile_info(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            email = received_json_data['email']
            try:
                user = User.objects.get(email = email)
                return Response({"message" : errorEmailExist, "status" : "0"}, status=status.HTTP_409_CONFLICT)
            except:
                user2 = User.objects.filter(id = user.id).update(email = received_json_data['email'],
                                    first_name = received_json_data['first_name'],
                                    last_name = received_json_data['last_name'],
                                    phone = received_json_data['phone'],
                                    country = received_json_data['country'],
                                    city = received_json_data['city'],
                                    address = received_json_data['address'],
                                    zip = received_json_data['zip']
                                    )
                if user2:
                    if received_json_data['image'] is not None and received_json_data['image'] != "":
                        profilePicName = received_json_data['first_name']+'.jpg'
                        try:
                            format, tempString = request.data['image'].split(';base64,')
                        except:
                            tempString = ""
                        
                        if tempString == "":
                            tempString = request.data['profile_pic']
                        
                        image_64_decode = base64.decodestring(tempString) 
                        fh = default_storage.open("profilepic/" + user.id + "/" + profilePicName, 'w')  # create a writable image and write the decoding result
                        fh.write(image_64_decode)
                        fh.close()
                        profile_pic_url = settings.MEDIA_URL + "profilepic/" + user.id + "/" + profilePicName
                        User.objects.filter(id = user.id).update(image = profile_pic_url)
                    
                    user = User.objects.get(id = user.id)
                    user_detail = {"last_login" : user.last_login,
                                    "username" : user.username,
                                    "first_name" : user.first_name,
                                    "last_name" : user.last_name,
                                    "email" : user.email,
                                    "date_joined" : user.date_joined,
                                    "phone" : user.phone,
                                    "country" : user.country,
                                    "city" : user.city,
                                    "address" : user.address,
                                    "zip" : user.zip,
                                    "image" : user.image,
                                    "sign_up_status" : user.sign_up_status,
                                    "social_id" : user.social_id}
                    return Response({"message" : addSuccessMessage, "data" : user_detail, "status" : "1"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)