#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationCabinet.generated.h"
class UStaticMeshComponent;
class UBoxComponent;
class UWidgetComponent;
class UAudioComponent;
class USoundBase;
class SWidget;
class STextBlock;

/** A fitted storage mechanism with authored pivot and per-piece collision. */
UCLASS(Blueprintable)
class GAME_API AStationCabinet : public AActor
{
 GENERATED_BODY()
public:
 AStationCabinet();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void Tick(float DeltaSeconds) override;
 UFUNCTION(BlueprintCallable) bool TryInteract();
 UFUNCTION(BlueprintCallable,CallInEditor) void RebuildCollision();
 UFUNCTION(BlueprintPure) float GetOpenFraction() const { return Progress; }
 UFUNCTION(BlueprintPure) bool IsObstructed() const { return bObstructed; }
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USceneComponent> Pivot;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> MovingMesh;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Cam;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector CamLocation=FVector::ZeroVector;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<USoundBase> LatchSound;
 UFUNCTION(BlueprintPure) float GetCamRelease() const { return CamRelease; }
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UWidgetComponent> InteractionPrompt;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAudioComponent> MotionAudio;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bSliding=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float OpenAngle=-90;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector OpenOffset=FVector(0,-38,0);
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float SecondsToOpen=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FString DisplayName=TEXT("cabinet");
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector FocusLocation=FVector::ZeroVector;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> CollisionCenters;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> CollisionExtents;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<USoundBase> MovementSound;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<USoundBase> ClosingSound;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<TObjectPtr<USoundBase>> OpeningTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<TObjectPtr<USoundBase>> ClosingTakes;
private:
 TWeakObjectPtr<USoundBase> LastOpeningTake,LastClosingTake;
 UPROPERTY(Transient) TArray<TObjectPtr<UBoxComponent>> Boxes;
 TSharedPtr<SWidget> HintWidget;
 TSharedPtr<STextBlock> HintAction,HintDetail;
 float Progress=0,Target=0;
 float CamRelease=0;
 bool bWantsOpen=false,bObstructed=false;
 FTransform Pose(float Fraction) const;
 bool CanOccupy(float Fraction) const;
 bool HasFocus(class APlayerController* PC) const;
 void ShowHint(bool Visible);
};
