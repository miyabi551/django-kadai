# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # pyexpat.errorsではなくdjango.contribのmessagesを使用
from django.http import HttpResponseRedirect
from django.template.defaultfilters import date
import datetime
from .models import Employee, Tabyouin
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import json
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .models import Patient
from .models import Medication


def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        try:
            employee = Employee.objects.get(empid=user_id)  # empidをuser_idに変更

            if check_password(password, employee.emppasswd) or password == employee.emppasswd:

                if employee.emprole == 1:  # emproleをroleに変更
                    return render(request, 'kanrisya_login.html')
                elif employee.emprole == 2:
                    return render(request, 'uketuke_login.html')
                elif employee.emprole == 3:
                    return render(request, 'isya_login.html')

            else:
                messages.error(request, 'ユーザーIDかパスワードが正しくありません。')
                return render(request, 'login.html')

        except Employee.DoesNotExist:
            messages.error(request, 'ユーザーIDまたはパスワードが間違っています。')
            return render(request, 'login.html')

    return render(request, 'login.html')


def tourokukinou_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        # パスワードの確認
        if password != confirm_password:
            messages.error(request, 'パスワードが一致しません。')
            return render(request, 'tourokukinou.html')

        # 従業員をデータベースに登録
        try:
            new_employee = Employee.objects.create(
                empid=user_id,
                empfname=first_name,
                emplname=last_name,
                emppasswd=password,
                emprole=role
            )
            messages.success(request, '従業員が登録されました。')
            return render(request, 'tourokukinou.html')
        except Exception as e:
            messages.error(request, f'登録中にエラーが発生しました: {str(e)}')
            return render(request, 'tourokukinou.html')

    return render(request, 'tourokukinou.html')


def kanrisya_login_view(request):
    return render(request, 'kanrisya_login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'ログアウトしました。')
    return render(request, 'logout.html')


def tuika_view(request):
    if request.method == 'POST':
        tabyouin = {
            'tabyouinid': request.POST.get('tabyouinid'),
            'tabyouinmei': request.POST.get('tabyouinmei'),
            'tabyouinaddress': request.POST.get('tabyouinaddress'),
            'tabyouintel': request.POST.get('tabyouintel'),
            'tabyouinshihonkin': request.POST.get('tabyouinshihonkin'),
            'kyukyu': request.POST.get('kyukyu') == '1',
        }
        request.session['tabyouin'] = tabyouin
        return redirect('confirm_tabyouin')
    return render(request, 'tuika.html')


def confirm_tabyouin(request):
    tabyouin = request.session.get('tabyouin')
    if not tabyouin:
        return redirect('tuika')
    return render(request, 'confirm_tabyouin.html', {'tabyouin': tabyouin})


def confirm_tabyouin_submission(request):
    tabyouin_data = request.session.get('tabyouin')
    if tabyouin_data:
        tabyouin = Tabyouin(
            tabyouinid=tabyouin_data['tabyouinid'],
            tabyouinmei=tabyouin_data['tabyouinmei'],
            tabyouinaddress=tabyouin_data['tabyouinaddress'],
            tabyouintel=tabyouin_data['tabyouintel'],
            tabyouinshihonkin=tabyouin_data['tabyouinshihonkin'],
            kyukyu=tabyouin_data['kyukyu'],
        )
        tabyouin.save()
        del request.session['tabyouin']
        return render(request, 'confirmed.html')
    return HttpResponseRedirect('/tuika/')


def itiranhyouzi_view(request):
    tabyouins = Tabyouin.objects.values('tabyouinid', 'tabyouinmei', 'tabyouinaddress', 'tabyouintel',
                                        'tabyouinshihonkin', 'kyukyu')
    return render(request, 'itiranhyouzi.html', {'tabyouins': tabyouins})


def zyuusyokensaku(request):
    searched_tabyouinaddress = request.GET.get('tabyouinaddress', '')
    tabyouins = Tabyouin.objects.filter(tabyouinaddress__icontains=searched_tabyouinaddress)
    return render(request, 'zyuusyokensaku.html', {
        'tabyouins': tabyouins,
        'searched_tabyouinaddress': searched_tabyouinaddress
    })


def simeihenkou_view(request):
    if request.method == 'POST':
        empid = request.POST.get('empid')
        empfname = request.POST.get('empfname')
        emplname = request.POST.get('emplname')

        # データベース更新
        try:
            employee = Employee.objects.get(empid=empid)
            employee.empfname = empfname
            employee.emplname = emplname
            employee.save()
            return JsonResponse({'success': '名前が更新されました。'})
        except Employee.DoesNotExist:
            return JsonResponse({'error': '指定された従業員が見つかりません。'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'simeihenkou.html')


def update_employee_name(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            empid = data.get('empid')
            empfname = data.get('empfname')
            emplname = data.get('emplname')

            if empid:
                try:
                    employee = Employee.objects.get(empid=empid)
                    employee.empfname = empfname
                    employee.emplname = emplname
                    employee.save()
                    return JsonResponse({'message': '名前を変更しました。'})
                except Employee.DoesNotExist:
                    return JsonResponse({'error': '該当する従業員が見つかりません。'}, status=404)
            else:
                return JsonResponse({'error': '従業員IDを指定してください。'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '無効なJSONです。'}, status=400)
    return JsonResponse({'error': '不正なリクエストです。'}, status=400)


def change_password_admin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('userId')
        new_password = data.get('newPassword')

        try:
            user = User.objects.get(username=user_id)
            user.set_password(new_password)
            user.save()
            return JsonResponse({'message': 'パスワードが変更されました。'})
        except User.DoesNotExist:
            return JsonResponse({'error': '指定されたユーザーが見つかりません。'}, status=404)
    return JsonResponse({'error': '不正なリクエストです。'}, status=400)


@csrf_exempt
def change_password_employee(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            emp_id = data.get('empid')
            new_password = data.get('newPassword')

            employee = Employee.objects.get(empid=emp_id)
            employee.password = new_password
            employee.save()
            return JsonResponse({'message': 'パスワードが変更されました。'})
        except Employee.DoesNotExist:
            return JsonResponse({'error': '従業員が見つかりません。'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSONデータが無効です。'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': '不正なリクエストです。'}, status=400)


def uketuke_login(request):
    return render(request, 'uketuke_login.html')


def kanzyatouroku_view(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'confirm':
            # 確認画面表示用のデータを取得
            context = {
                'patid': request.POST.get('patid'),
                'patfname': request.POST.get('patfname'),
                'patlname': request.POST.get('patlname'),
                'hokenmei': request.POST.get('hokenmei'),
                'hokenexp': request.POST.get('hokenexp'),
                'confirmation': True
            }
            return render(request, 'kanzyatouroku.html', context)
        elif request.POST.get('action') == 'submit':
            # データベースに保存
            patient = Patient(
                patid=request.POST.get('patid'),
                patfname=request.POST.get('patfname'),
                patlname=request.POST.get('patlname'),
                hokenmei=request.POST.get('hokenmei'),
                hokenexp=request.POST.get('hokenexp')
            )
            patient.save()
            return redirect('success')  # 成功ページにリダイレクト
    else:
        context = {
            'patid': '',
            'patfname': '',
            'patlname': '',
            'hokenmei': '',
            'hokenexp': '',
            'confirmation': False
        }
        return render(request, 'kanzyatouroku.html', context)


def zyouhouhenkou_view(request):
    return render(request, 'zyouhouhenkou.html')


def kanzyakanri_view(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlname = request.POST.get('patlname')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')

        try:
            patient = Patient.objects.get(patid=patid, patfname=patfname, patlname=patlname)
            patient.hokenmei = hokenmei
            patient.hokenexp = hokenexp
            patient.save()
            messages.success(request, '保険証情報が正常に更新されました。')
            return redirect('kanzyakanri')
        except Patient.DoesNotExist:
            error_message = '指定された患者が見つかりません。'
            return render(request, 'kanzyakanri.html', {'error_message': error_message})
        except Exception as e:
            error_message = f'エラーが発生しました: {str(e)}'
            return render(request, 'kanzyakanri.html', {'error_message': error_message})

    return render(request, 'kanzyakanri.html')


def confirm_patient_insurance_change_view(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'confirm':
            try:
                patient = get_object_or_404(Patient, patid=request.POST.get('patid'))
                patient.hokenmei = request.POST.get('hokenmei')
                patient.hokenexp = request.POST.get('hokenexp')

                context = {
                    'patient': patient,
                }
                return render(request, 'kanzyakanri.html', context)
            except Exception as e:
                return render(request, 'error.html', {'error_message': str(e)})

        elif request.POST.get('action') == 'submit':
            try:
                patient = get_object_or_404(Patient, patid=request.POST.get('patid'))
                patient.hokenmei = request.POST.get('hokenmei')
                patient.hokenexp = request.POST.get('hokenexp')
                patient.save()

                return redirect('kanzyakanri')
            except Exception as e:
                return render(request, 'error.html', {'error_message': str(e)})

    return redirect('kanzyakanri')


def hokensyokensaku_view(request):
    patients = []
    if 'searchDate' in request.GET:
        search_date = request.GET.get('searchDate')
        if search_date:
            patients = Patient.objects.filter(
                hokenexp__lt=search_date,

            )
    return render(request, 'hokensyokensaku.html', {'patients': patients})


def isya_login_view(request):
    return render(request, 'isya_login.html')


def kanzyakensaku_view(request):
    patients = []
    if request.GET:
        patfname = request.GET.get('patfname', '')
        patlname = request.GET.get('patlname', '')
        if patfname or patlname:
            patients = Patient.objects.filter(
                patfname__icontains=patfname,
                patlname__icontains=patlname
            )
    return render(request, 'kanzyakensaku.html', {'patients': patients})


def kusuri_tuika(request):
    if request.method == 'POST':
        patid = request.POST['patient_id']
        patfname = request.POST['patient_fname']
        patlname = request.POST['patient_lname']
        hokenmei = request.POST['kanzyahokenmei']
        hokenexp = request.POST['kanzyahokenexp']

        medicineids = request.POST.getlist('kanzyamedids[]')
        medicinenames = request.POST.getlist('kanzyamednames[]')
        medunits = request.POST.getlist('medunits[]')

        print(f'患者ID: {patid}')
        print(f'患者姓: {patfname}')
        print(f'患者名: {patlname}')
        print(f'保険証記号番号: {hokenmei}')
        print(f'保険証有効期限: {hokenexp}')

        for i in range(medicineids):
            medicineid = medicineids[i]
            medicinename = medicinenames[i]
            medunit = medunits[i]

            print(f'薬剤ID: {medicineid}, 薬剤名: {medicinename}, 数量: {medunit}')

            Medication.objects.create(
                kanzyaid=patid,
                kanzyafname=patfname,
                kanzyalname=patlname,
                kanzyahokenmei=hokenmei,
                kanzyahokenexp=hokenexp,
                kanzyamedid=medicineid,
                kanzyamedname=medicinename,
                medcount=medunit
            )

        return redirect(reverse('success_k'))  # 適切なリダイレクト先を設定してください
    return render(request, 'kusuri_tuika.html')


def kusuri_tuikakakunin_view(request):
    return render(request, 'kusuri_tuikakakunin.html')


def kusuri_sakuzyo_view(request):
    if request.method == 'POST':
        medication_id = request.POST.get('medication_id', '')
        try:
            medication = Medication.objects.get(pk=medication_id)
            medication.delete()
            return redirect('kusuri_sakuzyo')  # 薬剤削除画面にリダイレクト
        except Medication.DoesNotExist:
            return HttpResponse("薬剤が見つかりませんでした。", status=404)

    medications = Medication.objects.all()
    return render(request, 'kusuri_sakuzyo.html', {'medications': medications})


def syoti_kakutei_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == '処置確定':
            medication_ids = request.POST.getlist('medication_ids[]')
            medication_names = request.POST.getlist('medication_names[]')
            quantities = request.POST.getlist('quantities[]')

            for medicineid, medicinename, quantity in zip(medication_ids, medication_names, quantities):
                Medication.objects.create(medicineid=medicineid, medicinename=medicinename, unit=quantity)

            return redirect('kusuri_tuika')  # 処置確定後にリダイレクトするページを指定

        elif action == '薬剤選択画面へ戻る':
            return redirect('kusuri_tuika')

    return redirect('kusuri_tuika')


def medication_confirmation_view(request):
    selected_medications = request.POST.getlist('selected_medications[]')
    return render(request, 'medication_confirmation.html', {'selected_medications': selected_medications})
