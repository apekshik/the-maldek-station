#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationInspectable.generated.h"

class UStaticMeshComponent;
class USoundBase;
class APlayerController;

/** A physical prop that can be examined and returned without changing its world placement. */
UCLASS(Blueprintable)
class GAME_API AStationInspectable : public AActor
{
 GENERATED_BODY()
public:
 AStationInspectable();
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Inspection") TObjectPtr<UStaticMeshComponent> Mesh;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection") FText DisplayName;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection", meta=(MultiLine=true)) FText Description;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection") bool bCanInspect=true;
 /** Orientation relative to the inspection camera (X faces away from the player). */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection") FRotator InspectionRotation=FRotator(0,180,0);
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection|Audio") TObjectPtr<USoundBase> PickupSound;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection|Audio") TObjectPtr<USoundBase> ReturnSound;
 UFUNCTION(BlueprintImplementableEvent, Category="Inspection") void OnInspectionStarted(APlayerController* Player);
 UFUNCTION(BlueprintImplementableEvent, Category="Inspection") void OnInspectionFinished(APlayerController* Player);
};
