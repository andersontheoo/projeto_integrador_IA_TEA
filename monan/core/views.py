from django.shortcuts import render, redirect, get_object_or_404
# Funções utilitárias do Django para renderizar templates,
# redirecionar requisições e obter objetos do banco com validação 404.

from django.contrib.auth.decorators import login_required
# Decorator que garante que apenas usuários autenticados
# possam acessar as views protegidas.

from django.contrib import messages
# Framework de mensagens do Django, usado para exibir feedback
# ao usuário (sucesso, erro, avisos).

from .models import EEGFile, Analysis, ReportConfig
# Importação dos modelos principais utilizados pelas views.

import os
# Utilizado para manipulação de caminhos e extensões de arquivos.

import random
# Utilizado temporariamente para simular o comportamento da IA
# enquanto o WEKA via CSI não está integrado.


# ============================================================
# IMPORTANTE: Importar os decoradores de segurança personalizados
# ============================================================
from .decorators import can_upload, can_audit
# Decoradores responsáveis por controlar permissões de acesso
# com base no perfil do usuário (médico, auditor ou admin).


# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
@login_required
def dashboard(request):
    # Obtém o perfil do usuário autenticado, se existir
    profile = getattr(request.user, 'profile', None)
    
    # Auditor ou Admin têm visão global para monitoramento
    if profile and (profile.is_auditor or profile.is_admin):
        # Busca os 10 arquivos mais recentes de todo o sistema
        files = EEGFile.objects.all().order_by('-uploaded_at')[:10]

        # O modo 'audit' é usado no template para ajustar a interface
        context = {'files': files, 'mode': 'audit'}
    else:
        # Médico visualiza apenas seus próprios arquivos
        files = EEGFile.objects.filter(user=request.user).order_by('-uploaded_at')[:10]

        # O modo 'doctor' limita funcionalidades no template
        context = {'files': files, 'mode': 'doctor'}
        
    # Renderiza o dashboard com contexto dinâmico por perfil
    return render(request, 'dashboard.html', context)


# ============================================================
# UPLOAD DE ARQUIVOS (ZONA DE PERIGO)
# Acesso restrito a Médico e Admin
# ============================================================
import uuid

@login_required
@can_upload 
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Validação rigorosa da extensão
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        allowed_extensions = ['.gdf', '.dta']

        if ext not in allowed_extensions:
            messages.error(
                request,
                "Formato inválido. Apenas arquivos .gdf ou .dta são permitidos."
            )
            return redirect('upload_file')

        # Renomeação segura do arquivo com UUID
        new_filename = f"{uuid.uuid4()}{ext}"
        uploaded_file.name = new_filename

        # Criação do registro no banco de dados
        EEGFile.objects.create(
            user=request.user,
            file=uploaded_file,
            original_name=new_filename,
            size_bytes=uploaded_file.size,
            status='pending'
        )

        messages.success(request, "Arquivo enviado com sucesso!")
        return redirect('request_analysis')

    return render(request, 'upload.html')


# ============================================================
# SOLICITAÇÃO DE ANÁLISE
# ============================================================
@login_required
@can_upload
def request_analysis(request):
    # Lista apenas arquivos do usuário que ainda não possuem análise
    # Evita duplicidade de processamento
    user_files = EEGFile.objects.filter(
        user=request.user,
        analysis__isnull=True
    ).order_by('-uploaded_at')

    # Renderiza a tela de solicitação de análise
    return render(request, 'request_analysis.html', {'user_files': user_files})


# ============================================================
# EXECUÇÃO DA ANÁLISE (SIMULADA)
# ============================================================
from core.services.ml_api import run_eeg_analysis

@login_required
@can_upload
def analyze_file(request, file_id):
    eeg_file = get_object_or_404(EEGFile, id=file_id)

    # Segurança: médico só analisa os próprios arquivos
    if eeg_file.user != request.user and not request.user.profile.is_admin:
        messages.error(request, "Você não tem permissão para analisar este arquivo.")
        return redirect('dashboard')

    try:
        # Caminho físico do arquivo no sistema
        file_path = eeg_file.file.path

        # Execução da IA (simulada ou WEKA futuramente)
        result = run_eeg_analysis(file_path)

        # Criação do registro da análise
        analysis = Analysis.objects.create(
            eeg_file=eeg_file,
            classification=result["classification"],
            confidence=result["confidence"]
        )

        # Atualiza status do arquivo
        eeg_file.status = 'completed'
        eeg_file.save()

        messages.success(request, "Análise concluída com sucesso.")
        return redirect('result_view', analysis_id=analysis.id)

    except Exception as e:
        # Em caso de erro, registra falha
        eeg_file.status = 'error'
        eeg_file.save()

        messages.error(
            request,
            f"Erro ao processar a análise: {str(e)}"
        )
        return redirect('dashboard')



# ============================================================
# VISUALIZAÇÃO DO RESULTADO DA ANÁLISE
# ============================================================
@login_required
def result_view(request, analysis_id):
    # Obtém o perfil do usuário autenticado
    profile = request.user.profile
    
    # Auditor e Admin podem visualizar qualquer análise
    if profile.is_auditor or profile.is_admin:
        analysis = get_object_or_404(Analysis, id=analysis_id)
    else:
        # Médico só pode visualizar análises dos seus próprios arquivos
        analysis = get_object_or_404(
            Analysis,
            eeg_file__user=request.user,
            id=analysis_id
        )
        
    # Renderiza o resultado da análise
    return render(request, 'result.html', {'analysis': analysis})


# ============================================================
# HISTÓRICO / AUDITORIA DE LAUDOS
# ============================================================
@login_required
def report_history(request):
    profile = request.user.profile
    
    # Auditor/Admin possuem visão global do sistema
    if profile.is_auditor or profile.is_admin:
        analyses = Analysis.objects.all().order_by('-analyzed_at')
        title = "Auditoria Global de Laudos"
    else:
        # Médico visualiza apenas seus próprios laudos
        analyses = Analysis.objects.filter(
            eeg_file__user=request.user
        ).order_by('-analyzed_at')
        title = "Meus Laudos"
        
    # Renderiza a tela de histórico com título dinâmico
    return render(
        request,
        'history.html',
        {'analyses': analyses, 'page_title': title}
    )


# ============================================================
# CONFIGURAÇÕES DE RELATÓRIO
# ============================================================
@login_required
def report_settings(request):
    # Obtém ou cria configuração individual para o usuário
    config, created = ReportConfig.objects.get_or_create(user=request.user)

    # Atualiza configurações caso a requisição seja POST
    if request.method == 'POST':
        config.format = request.POST.get('format')
        config.frequency = request.POST.get('frequency')
        config.save()
        messages.success(request, "Configurações salvas.")

    # Renderiza a tela de configurações
    return render(request, 'report_settings.html', {'config': config})


# ============================================================
# PRÉ-VISUALIZAÇÃO DE RELATÓRIO
# ============================================================
@login_required
def report_preview(request, analysis_id):
    # Mesma regra de acesso do result_view
    profile = request.user.profile

    if profile.is_auditor or profile.is_admin:
        analysis = get_object_or_404(Analysis, id=analysis_id)
    else:
        analysis = get_object_or_404(
            Analysis,
            eeg_file__user=request.user,
            id=analysis_id
        )
        
    # Renderiza a pré-visualização do relatório
    return render(
        request,
        'report_preview.html',
        {'analysis_id': analysis.id}
    )


# ============================================================
# GERAÇÃO / DOWNLOAD DE PDF
# ============================================================
@login_required
def report_pdf(request, analysis_id):
    from django.http import HttpResponse
    # Importação local do HttpResponse para retorno direto do PDF

    # Auditor/Admin podem gerar PDF de qualquer análise
    profile = request.user.profile

    if profile.is_auditor or profile.is_admin:
        analysis = get_object_or_404(Analysis, id=analysis_id)
    else:
        analysis = get_object_or_404(
            Analysis,
            eeg_file__user=request.user,
            id=analysis_id
        )
        
    # Retorno simulado do PDF (placeholder)
    return HttpResponse(
        f"PDF do exame {analysis.eeg_file.original_name}",
        content_type='application/pdf'
    )
