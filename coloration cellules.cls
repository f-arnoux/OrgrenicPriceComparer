VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Feuil7"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Sub HighlightMinimum()
    Dim ws As Worksheet
    Dim rng As Range
    Dim rowRange As Range
    Dim minValue As Double
    Dim colIndexes As Variant
    Dim i As Long
    Dim cellValue As Double
    Dim hasNumericValue As Boolean
    Dim cleanedValue As String

    ' Définir la feuille et la plage (modifiez selon vos besoins)
    Set ws = ThisWorkbook.Sheets("November 2024") ' Changez le nom de la feuille si nécessaire
    Set rng = ws.Range("B5:L400") ' Changez la plage si nécessaire

    ' Indices des colonnes à comparer (B, D, F, H, J, L)
    colIndexes = Array(1, 3, 5, 7, 9, 11)

    ' Parcourir chaque ligne dans la plage
    For Each rowRange In rng.Rows
        hasNumericValue = False
        minValue = 0 ' Initialisation par défaut

        ' Trouver le minimum dans les colonnes spécifiques
        For i = LBound(colIndexes) To UBound(colIndexes)
            With rowRange.Cells(1, colIndexes(i))
                ' Vérifier si la cellule contient une valeur numérique
                cleanedValue = Trim(.Value) ' Supprimer les espaces superflus

                If Len(cleanedValue) > 0 Then
                    ' Remplacer la virgule par un point et convertir en nombre
                    cleanedValue = Replace(cleanedValue, ".", ",")
                    If IsNumeric(cleanedValue) Then
                        cellValue = CDbl(cleanedValue) ' Convertir en numérique

                        ' Si c'est la première valeur numérique, on l'initialise comme minValue
                        If Not hasNumericValue Then
                            minValue = cellValue
                            hasNumericValue = True
                        Else
                            ' Sinon on met à jour le minimum
                            minValue = WorksheetFunction.Min(minValue, cellValue)
                        End If
                    End If
                End If
            End With
        Next i

        ' Si aucune valeur numérique n'est trouvée dans cette ligne, passer à la ligne suivante
        If Not hasNumericValue Then
            GoTo NextRow
        End If

        ' Parcourir les colonnes spécifiques pour mettre en surbrillance
        For i = LBound(colIndexes) To UBound(colIndexes)
            With rowRange.Cells(1, colIndexes(i))
                ' Vérifier à nouveau si la cellule contient une valeur numérique valide
                cleanedValue = Trim(.Value) ' Supprimer les espaces superflus
                If Len(cleanedValue) > 0 Then
                    ' Remplacer la virgule par un point et convertir en nombre
                    cleanedValue = Replace(cleanedValue, ".", ",")
                    If IsNumeric(cleanedValue) Then
                        cellValue = CDbl(cleanedValue) ' Convertir en numérique

                        If cellValue = minValue Then
                            .Interior.Color = RGB(255, 255, 0) ' Mettre en jaune
                        Else
                            .Interior.Color = RGB(255, 255, 255) ' Réinitialiser la couleur
                        End If
                    End If
                End If
            End With
        Next i

NextRow:
    Next rowRange

    MsgBox "Mise en surbrillance terminée !", vbInformation
End Sub

