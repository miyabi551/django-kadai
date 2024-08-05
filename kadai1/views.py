# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # pyexpat.errorsではなくdjango.contribのmessagesを使用
from django.http import HttpResponseRedirect
from .models import Employee, Tabyouin
from django.contrib.auth.hashers import check_password
from datetime import date
from django.http import JsonResponse
import json
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .models import Patient
from .models import Medication, Medication_K


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
            messages.success(request, '登録しました。')
            return render(request, 'tourokukinou.html')
        except Exception as e:
            messages.error(request, 'エラーが発生しました。')
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
        tabyouinid = request.POST.get('tabyouinid')
        tabyouinmei = request.POST.get('tabyouinmei')
        tabyouinaddress = request.POST.get('tabyouinaddress')
        tabyouintel = request.POST.get('tabyouintel')
        tabyouinshihonkin = request.POST.get('tabyouinshihonkin')
        kyukyu = request.POST.get('kyukyu') == '1'

        # モデルにデータを保存
        if not tabyouinid or not tabyouinmei or not tabyouinaddress or not tabyouintel or not tabyouinshihonkin:
            messages.error(request, '全ての必須項目を入力してください。')
        if Tabyouin.objects.filter(tabyouinid=tabyouinid):
            messages.error(request, '同じIDは登録できません。')

        else:
            try:
                new_tabyouin = Tabyouin(
                    tabyouinid=tabyouinid,
                    tabyouinmei=tabyouinmei,
                    tabyouinaddress=tabyouinaddress,
                    tabyouintel=tabyouintel,
                    tabyouinshihonkin=tabyouinshihonkin,
                    kyukyu=kyukyu
                )
                new_tabyouin.save()
                messages.success(request, '登録しました。')
                return redirect('itiranhyouzi')
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {e}')

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

        if not empid or not empfname or not emplname:
            return render(request, 'error_e.html', {'error': 'すべてのフィールドを入力してください。'})

        try:
            employee = Employee.objects.get(empid=empid)
            employee.empfname = empfname
            employee.emplname = emplname
            employee.save()
            return render(request, 'success_e.html', {'success': '名前が更新されました。'})
        except Employee.DoesNotExist:
            return render(request, 'error_e.html', {'error': '指定された従業員が見つかりません。'})
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
        action = request.POST.get('action')
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlname = request.POST.get('patlname')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')

        if action == 'confirm':
            # 患者IDの重複チェック
            if Patient.objects.filter(patid=patid).exists():
                messages.error(request, "このIDは既に登録されています。")
                return render(request, 'kanzyatouroku.html', {
                    'patid': patid,
                    'patfname': patfname,
                    'patlname': patlname,
                    'hokenmei': hokenmei,
                    'hokenexp': hokenexp,
                    'confirmation': False
                })

                # 同姓同名の重複チェック
            if Patient.objects.filter(patfname=patfname, patlname=patlname).exists():
                messages.error(request, "同じ姓と名の患者が既に登録されています。")
                return render(request, 'kanzyatouroku.html', {
                    'patid': patid,
                    'patfname': patfname,
                    'patlname': patlname,
                    'hokenmei': hokenmei,
                    'hokenexp': hokenexp,
                    'confirmation': False
                })

            # 有効期限の日付チェック
            if hokenexp and date.fromisoformat(hokenexp) < date.today():
                messages.error(request, "有効期限は今日以降の日付で入力してください。")
                return render(request, 'kanzyatouroku.html', {
                    'patid': patid,
                    'patfname': patfname,
                    'patlname': patlname,
                    'hokenmei': hokenmei,
                    'hokenexp': hokenexp,
                    'confirmation': False
                })

            # 確認画面表示用のデータを取得
            context = {
                'patid': patid,
                'patfname': patfname,
                'patlname': patlname,
                'hokenmei': hokenmei,
                'hokenexp': hokenexp,
                'confirmation': True
            }
            return render(request, 'kanzyatouroku.html', context)

        elif action == 'submit':
            # データベースに保存
            patient = Patient(
                patid=patid,
                patfname=patfname,
                patlname=patlname,
                hokenmei=hokenmei,
                hokenexp=hokenexp
            )
            patient.save()
            messages.success(request, "患者情報が正常に登録されました。")
            return redirect('success')  # 成功ページにリダイレクト

    # 初期表示またはエラー時のデフォルト値
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
    if request.method == 'POST':
        empid = request.POST.get('empid')
        emppasswd1 = request.POST.get('emppasswd1')
        emppasswd2 = request.POST.get('emppasswd2')

        if not empid or not emppasswd1 or not emppasswd2:
            messages.error(request, 'すべてのフィールドを入力してください。')
            return render(request, 'zyouhouhenkou.html')

        if emppasswd1 != emppasswd2:
            messages.error(request, 'パスワードが一致しません。')
            return render(request, 'zyouhouhenkou.html')

        try:
            employee = Employee.objects.get(empid=empid)
            employee.emppasswd = emppasswd1
            employee.save()
            messages.success(request, 'パスワードが更新されました。')
            return redirect('uketuke_login')
        except Employee.DoesNotExist:
            messages.error(request, '指定された従業員が見つかりません。')
            return render(request, 'zyouhouhenkou.html')

    return render(request, 'zyouhouhenkou.html')


def kanzyakanri(request):
    if request.method == 'GET' and 'action' in request.GET and request.GET['action'] == 'confirm':
        patid = request.GET.get('patid')
        new_hokenmei = request.GET.get('hokenmei')
        new_hokenexp = request.GET.get('hokenexp')

        if not all([patid, new_hokenmei, new_hokenexp]):
            messages.error(request, '患者IDと保険証記号番号と有効期限を入力してください。')
            return redirect('kanzyakanri')

        if len(new_hokenmei) > 10:
            messages.error(request, '保険証記号番号は10文字以内で入力してください。')
            return redirect('kanzyakanri')

        try:
            new_hokenexp_date = date.fromisoformat(new_hokenexp)
            if new_hokenexp_date < date.today():
                messages.error(request, '有効期限は今日以降の日付を設定してください。')
                return redirect('kanzyakanri')

            # 他の患者の有効期限と重複しないことを確認
            if Patient.objects.filter(hokenexp=new_hokenexp).exists():
                messages.error(request, '同じ有効期限が既に存在します。他の日付を選択してください。')
                return redirect('kanzyakanri')

                # 他の患者で同じhokenmeiが使われていないことを確認
            if Patient.objects.filter(hokenmei=new_hokenmei).exclude(patid=patid).exists():
                messages.error(request,'この保険証記号番号は既に他の患者で使用されています。別の番号を入力してください。')
                return redirect('kanzyakanri')

            # 新しい値を設定
            patient = Patient.objects.get(patid=patid)
            patient.hokenmei = new_hokenmei
            patient.hokenexp = new_hokenexp
            patient.save()

            # 変更が完了した後のリダイレクト
            messages.success(request, '保険証の変更が成功しました。')
            return redirect('kanzyakanri')  # 変更が完了した後のリダイレクト先を適宜設定してください

        except Patient.DoesNotExist:
            messages.error(request, '該当する患者が見つかりませんでした。')
            return redirect('kanzyakanri')

    # Patientデータをすべて取得してテンプレートに渡す
    patients = Patient.objects.all()
    return render(request, 'kanzyakanri.html', {'patients': patients})


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


def kusuri_touyo(request):
    if request.method == 'POST':
        medicinenames = request.POST.getlist('kanzyamednames[]')
        medcounts = request.POST.getlist('medcounts[]')
        patid = request.POST.get('patid')

        patfname = request.POST.get('patfname') or request.GET.get('patfname')
        patlname = request.POST.get('patlname') or request.GET.get('patlname')

        # 患者IDの確認
        if not patid or not Patient.objects.filter(patid=patid).exists():
            messages.error(request, '患者IDが無効です。')
            return render(request, 'kusuri_touyo.html', {
                'error': '患者IDが無効です。',
                'all_medications': Medication.objects.all(),
                'medications': Medication_K.objects.all(),
                'patid': request.GET.get('patid'),
                'patfname': request.GET.get('patfname'),
                'patlname': request.GET.get('patlname')
            })

        # 薬剤情報の保存
        for i in range(len(medicinenames)):
            medicinename = medicinenames[i]
            medcount = medcounts[i]

            # 薬剤名の存在確認
            medication = Medication.objects.filter(medicinename=medicinename).first()
            if medication:
                Medication_K.objects.create(
                    kanzyaid=patid,
                    kanzyasei=patfname,
                    kanzyamei=patlname,
                    kusuriname=medicinename,
                    suuryou=medcount
                )
            else:
                messages.error(request, '無効な薬剤名です。')
                return render(request, 'kusuri_touyo.html', {
                    'all_medications': Medication.objects.all(),
                    'medications': Medication_K.objects.all(),
                    'patid': request.GET.get('patid'),
                    'patfname': request.GET.get('patfname'),
                    'patlname': request.GET.get('patlname')
                })

        messages.success(request, '薬剤情報が正常に登録されました。')
        return redirect('success_k')

    context = {
        'all_medications': Medication.objects.all(),
        'medications': Medication_K.objects.all(),
        'patid': request.GET.get('patid'),
        'patfname': request.GET.get('patfname'),
        'patlname': request.GET.get('patlname')
    }
    return render(request, 'kusuri_touyo.html', context)


def kusuri_tuikakakunin_view(request):
    return render(request, 'kusuri_tuikakakunin.html')


def kusuri_tuika(request):
    if request.method == 'POST':
        medicinename = request.POST.get('medicinename')
        unit = request.POST.get('unit')

        if medicinename:
            # 薬剤名の重複を防ぐために、既に存在するかを確認
            if Medication.objects.filter(medicinename=medicinename, unit=unit).exists():
                messages.error(request, 'この薬剤名は既に登録されています。')
                return redirect('kusuri_tuika')

            # 薬剤を作成し保存
            Medication.objects.create(medicinename=medicinename, unit=unit)
            messages.success(request, '薬剤が正常に追加されました。')
        else:
            messages.error(request, '薬剤名を入力してください。')

        return redirect('kusuri_tuika')

    return render(request, 'kusuri_tuika.html')


def kusuri_sakuzyo(request):
    if request.method == 'POST':
        medication_id = request.POST.get('medication_id')
        try:
            medication = Medication.objects.get(pk=medication_id)
            medication.delete()
            messages.success(request, '薬剤が正常に削除されました。')
        except Medication.DoesNotExist:
            messages.error(request, '指定された薬剤が見つかりません。')
        return redirect('kusuri_sakuzyo')

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
