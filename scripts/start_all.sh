#!/bin/bash
echo "🚀 Lancement des agents du SOC IA Unified..."

# On définit la racine du projet de manière dynamique
PROJECT_ROOT="/home/chaimae/soc-ia-unified"
cd $PROJECT_ROOT

# Export du PYTHONPATH pour que les agents trouvent le dossier 'common'
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT/agents

# Lancement des agents avec gestion du répertoire de travail
# Le log_tailer et collector ont besoin de trouver 'config/config.yaml'
nohup python3 agents/log_tailer/log_tailer.py > logs/log_tailer.log 2>&1 &
sleep 2
nohup python3 agents/collector/collector.py > logs/collector.log 2>&1 &
sleep 2
nohup python3 agents/analyzer/analyzer.py > logs/analyzer.log 2>&1 &
sleep 2

# Vérification du fichier supervisor avant lancement
if [ -f "$PROJECT_ROOT/agents/supervisor/supervisor.py" ]; then
    nohup python3 agents/supervisor/supervisor.py > logs/supervisor.log 2>&1 &
else
    echo "⚠️ Attention : agents/supervisor/supervisor.py introuvable."
fi

echo "✅ Tentative de lancement terminée."
echo "Consultez les fichiers dans le dossier 'logs/' pour vérifier les erreurs."
