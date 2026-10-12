# Projet_CATIE
Alerte et localisation d'une personne isolée

## Présentation
Une personne seule et isolée peut être sujet à un danger sans qu’elle puisse avoir le temps
de le signaler si elle est présente dans une zone où les réseaux cellulaires et le GNSS sont
indisponibles : par exemple lors de l'intervention d’une équipe de secours sur un sinistre
(bâtiment en feu, tunnel, souterrain).\
L’objet de ce projet est de développer un réseau de systèmes communicants permettant de
remonter l’information d’une alerte détectée sur un sujet ainsi que sa localisation. Le
système de détection devra détecter automatiquement une situation de danger (chute par
exemple) et remonter ces informations jusqu’au poste central via le réseau maillé
autodéployé par les membres de l’équipe.

## Tâches à réaliser
**Réseau maillé** : étude de Meshtastic et prise en main de la solution technique.\
**Localisation** : étude et expérimentation des solutions possibles avec le matériel et la
technologie existante.\
**Système porté** : détection de la perte de connaissance à partir de la centrale inertielle.\
**Gestion des alertes** : développement d’une IHM sur PC avec affichage de la localisation.

## Synoptique
![Synoptique du projet](/img/synoptique.png)

## Matériel
3x systèmes composés de cartes 6TRON (https://6tron.io) pour les nœuds du réseau :\
· **Zest_Core_FMLR-72** : carte programmable avec radio LoRa\
· **Zest_Sensor_IMU** : carte d’extension avec centrale inertielle pour la détection de
mouvement et de chute\
· **Zest_Battery_LiPo** : carte d’extension intégrant une batterie LiPo, son chargeur et sa
gauge\
Le poste central est composé de :\
· **Zest_Core_FMLR-72** : carte programmable avec radio LoRa
· un PC relié en USB avec la Zest_Core_FMLR-72
Le PC n’est pas fourni.
