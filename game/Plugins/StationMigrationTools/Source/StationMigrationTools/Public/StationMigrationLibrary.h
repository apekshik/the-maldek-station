#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "StationMigrationLibrary.generated.h"
class UMaterialInterface;
class UBlueprint;

UCLASS()
class STATIONMIGRATIONTOOLS_API UStationMigrationLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Isolate floating PIE from unrelated editor rendering; restores flags and removes only our override.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TArray<FString> SetEditorRenderingSuppressed(bool bSuppressed);

    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool IsBlueprintUpToDate(UBlueprint* Blueprint);

    // Changes the render target, independent of desktop window borders. Only PIE is eligible.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool SetPIERenderSize(int32 Width, int32 Height);

    // Raw engine measurements; enable stat unit before sampling. Missing values stay absent.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TMap<FString, double> CapturePIEFrameStats();

    // Wait for shader compilation and return real compile errors from the active RHI resources.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TArray<FString> ValidateMaterialShaders(const TArray<UMaterialInterface*>& Materials);

    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TArray<FString> GetLandscapeHeightmapPaths(AActor* LandscapeActor);

    // Exercises the existing input binding rather than changing flashlight visibility directly.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool SendPIEKey(FName KeyName, bool bPressed);

    // Route a pointer move through the PIE viewport without moving the desktop cursor.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool SendPIEMousePosition(float X, float Y);

    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TMap<FString, FTransform> GetFoliageInstanceTransforms(AActor* FoliageActor);

    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool MoveR12FoliageInstance(AActor* FoliageActor, const FString& TypePath,
        int32 InstanceIndex, FVector ExpectedLocation, FVector NewLocation);
};
